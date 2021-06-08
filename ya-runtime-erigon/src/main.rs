use futures::channel::oneshot;
use futures::FutureExt;
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::fs;
use std::path::PathBuf;
use std::process::Stdio;
use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering::Relaxed;
use tokio::process::{Child, Command};
use ya_runtime_sdk::*;

const AUTH_ERIGON_USER: &str = "erigolem";
const ERIGON_BIN: &str = "tg";
const RPCDAEMON_BIN: &str = "rpcdaemon";

const SUPPORTED_CHAINS: &[&str; 4] = &["goerli", "rinkeby", "ropsten", "kovan"];

//TODO: Make parameter list configurable for further extendability (Erigon & Rpcdaemon)
const RPCDAEMON_PARAMS: &[&str; 6] = &[
    "--private.api.addr",
    "localhost:9090",
    "--http.vhosts",
    "*",
    "--http.api",
    "eth,debug,net,trace,web3,tg",
];

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
            data_dir: "/data/turbo-geth".to_string(),
            passwd_tool_path: "htpasswd".to_string(),
            passwd_file_path: "/etc/nginx/erigon_htpasswd".to_string(),
            password_default_length: 15,
            erigon_http_addr: "127.0.0.1".to_string(),
            erigon_http_port: "8545".to_string(),
        }
    }
}

#[derive(Default, RuntimeDef)]
#[conf(ErigonConf)]
pub struct ErigonRuntime {
    seq: AtomicU64,
    erigon_pid: Option<Child>,
    rpcdaemon_pid: Option<Child>,
    erigon_password: Option<String>,
    erigon_chain_id: Option<String>,
}

impl Runtime for ErigonRuntime {
    const MODE: RuntimeMode = RuntimeMode::Server;

    fn deploy<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        let data_dir = ctx.conf.data_dir.clone();
        let chain_subdirs: Vec<PathBuf> = SUPPORTED_CHAINS
            .into_iter()
            .map(|d| prepare_data_dir_path(&data_dir, &d.to_string()))
            .collect();

        let data_dir_path = PathBuf::from(ctx.conf.data_dir.clone());
        let parent_data_dir = data_dir_path.as_path();
        if !(parent_data_dir.exists() && parent_data_dir.is_dir()) {
            panic!(
                "Configuration 'data_dir' directory has to exists and needs to contain
                 the directory for every supported network, named of the network"
            );
        }

        // create all supported chains data subdirs
        for pathbuf in chain_subdirs {
            if !&pathbuf.is_dir() {
                fs::create_dir(pathbuf.clone())
                    .unwrap_or_else(|_| panic!("Unable to create subdir {:?}", &pathbuf));
            }
        }

        async move {
            Ok(serialize::json::json!(
                {
                    "startMode":"blocking",
                    "valid":{"Ok":""},
                    "vols":[]
                }
            ))
        }
        .boxed_local()
    }

    fn start<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        let default_chain_id = "goerli".to_string();
        let chain_id = if let ya_runtime_sdk::cli::Command::Start { args } = &ctx.cli.command {
            parse_json(args.into_iter().next(), &default_chain_id)
        } else {
            default_chain_id
        };

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
        let data_dir_path = prepare_data_dir_path(&ctx.conf.data_dir.clone(), &chain_id);
        let mut erigon_pid = spawn_process(
            &mut Command::new(&path.join(ERIGON_BIN))
                .arg("--chain")
                .arg(chain_id.clone()),
            &data_dir_path,
            &[""; 0],
        )
        .expect("Erigon: Failed to spawn");

        let http_addr = ctx.conf.erigon_http_addr.clone();
        let http_port = ctx.conf.erigon_http_port.clone();
        let rpcd_pid = spawn_process(
            &mut Command::new(&path.join(RPCDAEMON_BIN))
                .arg("--http.addr")
                .arg(http_addr)
                .arg("--http.port")
                .arg(http_port),
            &data_dir_path,
            RPCDAEMON_PARAMS,
        );
        if !rpcd_pid.is_ok() {
            let _ = (&mut erigon_pid).kill();
        }
        let rpcd_pid = rpcd_pid.expect("RPC Daemon: Failed to spawn");

        self.erigon_pid = Some(erigon_pid);
        self.rpcdaemon_pid = Some(rpcd_pid);
        self.erigon_chain_id = Some(chain_id.clone());

        let chain_id_copied = chain_id.clone();
        async move { Ok(serialize::json::json!({ "network": chain_id_copied })) }.boxed_local()
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
        command: RunProcess,
        _mode: RuntimeMode,
        ctx: &mut Context<Self>,
    ) -> ProcessIdResponse<'a> {
        let seq = self.seq.fetch_add(1, Relaxed);
        let emitter = ctx.emitter.clone().unwrap();

        let (tx, rx) = oneshot::channel();
        let public_addr = ctx.conf.public_addr.clone();
        let password = self.erigon_password.clone();
        let chain_id = self.erigon_chain_id.clone();

        tokio::task::spawn_local(async move {
            // command execution started
            emitter.command_started(seq).await;
            // resolves the future returned by `run_command`
            let _ = tx.send(seq);

            let erigon_mock_data = serialize::json::json!(
                {
                    "status": "running",
                    "url": public_addr,
                    "network": chain_id,
                    "auth": {
                        "user": AUTH_ERIGON_USER,
                        "password": password
                    }
                }
            );
            let stdout = format!(
                "[{}] output for command: {:?}. ERIGON: {}",
                seq, command, erigon_mock_data
            )
            .as_bytes()
            .to_vec();

            tokio::time::delay_for(std::time::Duration::from_millis(1)).await;
            emitter.command_stdout(seq, stdout).await;
            emitter.command_stopped(seq, 0).await;
        });

        async move {
            // awaits `tx.send`
            Ok(rx.await.unwrap())
        }
        .boxed_local()
    }

    fn offer<'a>(&mut self, _ctx: &mut Context<Self>) -> OutputResponse<'a> {
        async move {
            Ok(serialize::json::json!(
                {
                    "constraints": "",
                    "properties": {}
                }
            ))
        }
        .boxed_local()
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

fn prepare_data_dir_path(parent_dir: &String, chain_id: &String) -> PathBuf {
    PathBuf::from(parent_dir).join(chain_id)
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

fn parse_json(config: Option<&String>, default_chain_id: &String) -> String {
    match config {
        None => default_chain_id.clone(),
        Some(json) => {
            let value: Value =
                serde_json::from_str(json).expect("Cannot parse config, assumes json string");
            let network = value["network"].as_str().unwrap();
            let _ = chain_id_valid(network).unwrap();
            network.to_owned()
        }
    }
}

fn chain_id_valid(chain_id: &str) -> Result<(), String> {
    match &chain_id.to_lowercase()[..] {
        "goerli" | "rinkeby" | "ropsten" | "kovan" => Ok(()),
        _ => Err("Unsupported chain id".to_owned()),
    }
}
