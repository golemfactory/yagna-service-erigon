use futures::channel::oneshot;
use futures::FutureExt;
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use serde::{Deserialize, Serialize};
use std::iter;
use std::path::PathBuf;
use std::process::Stdio;
use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering::Relaxed;
use tokio::process::{Child, Command};
use ya_runtime_sdk::*;

const AUTH_ERIGON_USER: &str = "erigolem";
const ERIGON_BIN: &str = "tg";
const RPCDAEMON_BIN: &str = "rpcdaemon";

//TODO: Make parameter list configurable for further extendability (Erigon & Rpcdaemon)
const RPCDAEMON_PARAMS: &[&str; 10] = &[
    "--private.api.addr",
    "localhost:9090",
    "--http.addr",
    "127.0.0.1",
    "--http.port",
    "8545",
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
}

impl Default for ErigonConf {
    fn default() -> Self {
        ErigonConf {
            public_addr: String::from("http://erigon.localhost:8545"),
            data_dir: String::from("/data/turbo-geth"),
            passwd_tool_path: String::from("/usr/bin/htpasswd"),
            passwd_file_path: String::from("/etc/nginx/erigon_htpasswd"),
            password_default_length: 15,
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
}

impl Runtime for ErigonRuntime {
    const MODE: RuntimeMode = RuntimeMode::Server;

    fn deploy<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        let data_dir_path = PathBuf::from(ctx.conf.data_dir.clone());
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

        // Generate user & password entry with passwd tool
        let mut rng = thread_rng();
        let password: String = iter::repeat(())
            .map(|()| rng.sample(Alphanumeric))
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
        let public_addr = ctx.conf.public_addr.clone();
        let password = self.erigon_password.clone();

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
