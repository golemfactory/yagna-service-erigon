use futures::channel::oneshot;
use futures::FutureExt;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::process::Stdio;
use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering::Relaxed;
use tokio::process::{Child, Command};
use ya_runtime_sdk::*;

const ERIGON_BIN: &str = "tg";
const RPCDAEMON_BIN: &str = "rpcdaemon";

//TODO: Make parameter list configurable for further extendability (Erigon & Rpcdaemon)
const RPCDAEMON_PARAMS: &[&str; 12] = &[
    "--private.api.addr",
    "localhost:9090",
    "--http.addr",
    "0.0.0.0",
    "--http.port",
    "8545",
    "--http.vhosts",
    "*",
    "--http.corsdomain",
    "*",
    "--http.api",
    "eth,debug,net,trace,web3,tg",
];

#[derive(Default, Deserialize, Serialize)]
pub struct ErigonConf {
    public_addr: Option<String>,
    data_dir: Option<String>,
}

#[derive(Default, RuntimeDef)]
#[conf(ErigonConf)]
pub struct ErigonRuntime {
    seq: AtomicU64,
    erigon_pid: Option<Child>,
    rpcdaemon_pid: Option<Child>,
    host: Option<String>,
}

impl Runtime for ErigonRuntime {
    const MODE: RuntimeMode = RuntimeMode::Server;

    fn deploy<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        let data_dir_path = PathBuf::from(
            ctx.conf
                .data_dir
                .clone()
                .expect("Configuration data_dir is missing"),
        );
        let parent_data_dir = data_dir_path.as_path();
        if !(parent_data_dir.exists() && parent_data_dir.is_dir()) {
            panic!(
                "Configuration 'data_dir' directory has to exists and needs to contain
                 the directory for every supported network, named of the network"
            );
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
        //TODO: Receive chain_id from start parameters when Yapapi ready
        // see: https://github.com/golemfactory/yapapi/issues/390
        let chain_id = String::from("goerli");
        let current_exe_path = std::env::current_exe().unwrap();
        let path = current_exe_path.parent().unwrap();

        let data_dir_path = prepare_data_dir_path(
            &ctx.conf
                .data_dir
                .clone()
                .expect("Configuration data_dir is missing"),
            &chain_id,
        );
        let mut erigon_pid = spawn_process(
            &mut Command::new(&path.join(ERIGON_BIN))
                .arg("--chain")
                .arg(chain_id),
            &data_dir_path,
            &[""; 0],
        )
        .expect("Erigon: Failed to spawn");

        let rpcd_pid = spawn_process(
            &mut Command::new(&path.join(RPCDAEMON_BIN)),
            &data_dir_path,
            RPCDAEMON_PARAMS,
        );
        if !rpcd_pid.is_ok() {
            let _ = (&mut erigon_pid).kill();
        }
        let rpcd_pid = rpcd_pid.expect("RPC Daemon: Failed to spawn");

        self.erigon_pid = Some(erigon_pid);
        self.rpcdaemon_pid = Some(rpcd_pid);

        self.host = ctx.conf.public_addr.clone();
        async move { Ok("start".into()) }.boxed_local()
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
        let public_addr = ctx
            .conf
            .public_addr
            .clone()
            .unwrap_or(String::from("unknown erigon address"));

        tokio::task::spawn_local(async move {
            // command execution started
            emitter.command_started(seq).await;
            // resolves the future returned by `run_command`
            let _ = tx.send(seq);

            let erigon_mock_data = serialize::json::json!(
                {
                    "status": "running",
                    "url": public_addr,
                    "auth": {
                        "user": "<BASIC-AUTH-USER>",
                        "password": "<BASIC-AUTH-PASS>"
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
