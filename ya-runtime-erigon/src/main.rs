use futures::FutureExt;
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Stdio;
use titlecase::titlecase;
use tokio::process::{Child, Command};
use ya_runtime_sdk::*;

const AUTH_ERIGON_USER: &str = "erigolem";
const ERIGON_BIN: &str = "erigon";
const RPCDAEMON_BIN: &str = "rpcdaemon";
const DEFAULT_CHAIN: Network = Network::Goerli;

//TODO: Make parameter list configurable for further extendability (Erigon & Rpcdaemon)
const RPCDAEMON_PARAMS: &[&str; 6] = &[
    "--private.api.addr",
    "localhost:9090",
    "--http.vhosts",
    "*",
    "--http.api",
    "eth,debug,net,trace,web3,tg",
];

#[macro_use]
extern crate custom_derive;
#[macro_use]
extern crate enum_derive;
custom_derive! {
#[derive(Debug, PartialEq, EnumDisplay, EnumFromStr, IterVariantNames(NetworkVariantNames))]
pub enum Network {
    Goerli,
    Rinkeby,
    Ropsten,
    Kovan
}}

#[derive(Deserialize, Serialize)]
pub struct ErigonConf {
    public_addr: String,
    data_dir: String,
    passwd_tool_path: String,
    passwd_file_path: String,
    password_default_length: usize,
    erigon_http_addr: String,
    erigon_http_port: String,
}

impl Default for ErigonConf {
    fn default() -> Self {
        ErigonConf {
            public_addr: "http://erigon.localhost:8545".to_string(),
            data_dir: "/data/erigon".to_string(),
            passwd_tool_path: "htpasswd".to_string(),
            passwd_file_path: "/etc/nginx/erigon_htpasswd".to_string(),
            password_default_length: 15,
            erigon_http_addr: "127.0.0.1".to_string(),
            erigon_http_port: "8555".to_string(),
        }
    }
}

#[derive(Default, RuntimeDef)]
#[conf(ErigonConf)]
pub struct ErigonRuntime {
    erigon_pid: Option<Child>,
    rpcdaemon_pid: Option<Child>,
    erigon_password: Option<String>,
    erigon_chain: Option<String>,
}

impl Runtime for ErigonRuntime {
    fn deploy<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        let data_dir = PathBuf::from(&ctx.conf.data_dir);

        // check if parent data directory exists
        if !(data_dir.exists() && data_dir.is_dir()) {
            panic!(
                "Configuration 'data_dir' directory has to exists and needs to contain
                 the directory for every supported network, named of the network"
            );
        }

        // create all supported chains data subdirs
        for chain_subdir in
            Network::iter_variant_names().map(|chain| chain_subdir(data_dir.as_path(), chain))
        {
            if !&chain_subdir.is_dir() {
                fs::create_dir(&chain_subdir)
                    .unwrap_or_else(|_| panic!("Unable to create subdir {:?}", &chain_subdir));
            }
        }

        async move { Ok(None) }.boxed_local()
    }

    fn start<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        let chain = get_chain_from_config(ctx.cli.command.args().into_iter().next());
        let chain = chain.to_string().to_lowercase();
        self.erigon_chain = Some(chain.clone());

        let current_exe_path = std::env::current_exe().unwrap();
        let path = current_exe_path.parent().unwrap();

        // Generate user & password entry with passwd tool
        let rng = thread_rng();
        let password: String = rng
            .sample_iter(Alphanumeric)
            .map(char::from)
            .take(ctx.conf.password_default_length)
            .collect();

        let _ = generate_password_file(
            &ctx.conf.passwd_tool_path,
            &ctx.conf.passwd_file_path,
            &password,
        )
        .expect("Unable to create passwd file");
        self.erigon_password = Some(password);

        // Spawn erigon processes
        let parent_dir = PathBuf::from(&ctx.conf.data_dir);
        let data_dir = chain_subdir(parent_dir.as_path(), &chain);
        let mut erigon_pid = spawn_process(
            &mut Command::new(&path.join(ERIGON_BIN))
                .arg("--chain")
                .arg(&chain),
            &data_dir,
            &[""; 0],
        )
        .expect("Erigon: Failed to spawn");

        let rpcd_pid = spawn_process(
            &mut Command::new(&path.join(RPCDAEMON_BIN))
                .arg("--http.addr")
                .arg(&ctx.conf.erigon_http_addr)
                .arg("--http.port")
                .arg(&ctx.conf.erigon_http_port),
            &data_dir,
            RPCDAEMON_PARAMS,
        );
        if !rpcd_pid.is_ok() {
            let _ = (&mut erigon_pid).kill();
        }
        let rpcd_pid = rpcd_pid.expect("RPC Daemon: Failed to spawn");

        self.erigon_pid = Some(erigon_pid);
        self.rpcdaemon_pid = Some(rpcd_pid);

        async move { Ok(Some(serialize::json::json!({ "network": chain }))) }.boxed_local()
    }

    fn stop<'a>(&mut self, _: &mut Context<Self>) -> EmptyResponse<'a> {
        let erigon_kill_ok = match &mut self.erigon_pid {
            Some(erigon_pid) => erigon_pid.kill().is_ok(),
            None => false,
        };
        let rpcd_kill_ok = match &mut self.rpcdaemon_pid {
            Some(rpcdaemon_pid) => rpcdaemon_pid.kill().is_ok(),
            None => false,
        };

        if !(erigon_kill_ok && rpcd_kill_ok) {
            panic!(
                "Unable to kill one of the processes. Erigon: {:?}, RpcDaemon: {:?}.",
                erigon_kill_ok, rpcd_kill_ok
            );
        }

        async move { Ok(()) }.boxed_local()
    }

    fn run_command<'a>(
        &mut self,
        _cmd: RunProcess,
        _mode: RuntimeMode,
        ctx: &mut Context<Self>,
    ) -> ProcessIdResponse<'a> {
        let erigon_status_data = serialize::json::json!(
            {
                "url": &ctx.conf.public_addr,
                "network": &self.erigon_chain,
                "auth": {
                    "user": AUTH_ERIGON_USER,
                    "password": &self.erigon_password
                }
            }
        );

        ctx.command(|mut run_ctx| async move {
            let stdout = format!("{}", erigon_status_data);
            run_ctx.stdout(stdout).await;
            Ok(())
        })
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    ya_runtime_sdk::run::<ErigonRuntime>().await
}

fn spawn_process(cmd: &mut Command, datadir: &PathBuf, params: &[&str]) -> std::io::Result<Child> {
    cmd.arg("--datadir")
        .arg(datadir)
        .args(params)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
}

fn chain_subdir(parent_dir: &Path, chain: &str) -> PathBuf {
    parent_dir.join(chain.to_lowercase())
}

fn generate_password_file(
    passwd_bin: &String,
    passwd_file: &String,
    password: &String,
) -> std::io::Result<Child> {
    Command::new(passwd_bin)
        .arg("-cb")
        .arg(passwd_file)
        .arg(AUTH_ERIGON_USER)
        .arg(password)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
}

fn get_chain_from_config(config: Option<&String>) -> Network {
    match config {
        None => DEFAULT_CHAIN,
        Some(json) => {
            let value: Value =
                serde_json::from_str(json).expect("Cannot parse config, assumes json string");
            let network = value["network"].as_str().unwrap();

            titlecase(network).parse().expect("Unsupported chain")
        }
    }
}
