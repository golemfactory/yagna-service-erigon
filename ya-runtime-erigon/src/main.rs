use futures::FutureExt;
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use serde::{Deserialize, Serialize};
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
    erigon_http_addr: String,
    erigon_http_port: String,
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
            erigon_http_addr: "127.0.0.1".to_string(),
            erigon_http_port: "8555".to_string(),
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
}

impl Runtime for ErigonRuntime {
    fn deploy<'a>(&mut self, _ctx: &mut Context<Self>) -> OutputResponse<'a> {
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

        async move { Ok(Some(serialize::json::json!({ "network": "mainnet" }))) }.boxed_local()
    }

    fn stop<'a>(&mut self, _: &mut Context<Self>) -> EmptyResponse<'a> {
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
