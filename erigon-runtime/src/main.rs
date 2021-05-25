use futures::channel::oneshot;
use futures::FutureExt;
use local_ipaddress;
use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering::Relaxed;
use tokio::process::{Child, Command};
use ya_runtime_sdk::*;

const ERIGON_BIN: &str = "tg";
const RPCDAEMON_BIN: &str = "rpcdaemon";

const ERIGON_PARAMS: &[&str; 2] = &["--datadir", "/data/turbo-geth/datadir"];
const RPCDAEMON_PARAMS: &[&str; 14] = &[
    "--datadir",
    "/data/turbo-geth/datadir",
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

#[derive(Default, RuntimeDef)]
pub struct ErigonRuntime {
    seq: AtomicU64,
    erigon_pid: Option<Child>,
    rpcdaemon_pid: Option<Child>,
}

impl Runtime for ErigonRuntime {
    const MODE: RuntimeMode = RuntimeMode::Server;

    fn deploy<'a>(&mut self, _: &mut Context<Self>) -> OutputResponse<'a> {
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

    fn start<'a>(&mut self, _: &mut Context<Self>) -> OutputResponse<'a> {
        let chain_id = String::from("goerli");
        let current_exe_path = std::env::current_exe().unwrap();
        let path = current_exe_path.parent().unwrap();

        let erigon_pid = Command::new(&path.join(ERIGON_BIN))
            .args(ERIGON_PARAMS)
            .arg("--chain")
            .arg(chain_id)
            .spawn()
            .expect("Erigon: Failed to spawn");

        let rpcd_pid = Command::new(&path.join(RPCDAEMON_BIN))
            .args(RPCDAEMON_PARAMS)
            .spawn()
            .expect("RPC Daemon: Failed to spawn");

        self.erigon_pid = Some(erigon_pid);
        self.rpcdaemon_pid = Some(rpcd_pid);

        async move { Ok("start".into()) }.boxed_local()
    }

    fn stop<'a>(&mut self, _: &mut Context<Self>) -> EmptyResponse<'a> {
        if let Some(erigon_pid) = &mut self.erigon_pid {
            erigon_pid.kill().unwrap();
        }
        if let Some(rpcd_pid) = &mut self.rpcdaemon_pid {
            rpcd_pid.kill().unwrap();
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

        tokio::task::spawn_local(async move {
            // command execution started
            emitter.command_started(seq).await;
            // resolves the future returned by `run_command`
            let _ = tx.send(seq);

            let erigon_mock_data = serialize::json::json!(
                {
                    "status": "running",
                    "url": format!("http://{}:8545", local_ipaddress::get().unwrap()),
                    "secret": "THE SECRET AUTH"
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
