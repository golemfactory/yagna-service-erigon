use futures::{FutureExt, TryFutureExt};
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use std::io;
use std::path::{Path, PathBuf};
use std::process::Stdio;
use tokio::fs::OpenOptions;
use tokio::process::{Child, Command};
use ya_runtime_sdk::*;

const AUTH_ERIGON_USER_PREFIX: &str = "erigolem";

#[derive(Deserialize, Serialize)]
pub struct ErigonConf {
    erigon_http_addr: String,
    erigon_http_port: String,
    public_addr: String,
    passwd_tool_path: String,
    passwd_file_path: String,
    password_default_length: usize,
}

impl Default for ErigonConf {
    fn default() -> Self {
        ErigonConf {
            erigon_http_addr: "127.0.0.1".to_string(),
            erigon_http_port: "8555".to_string(),
            public_addr: "http://erigon.localhost:8545".to_string(),
            passwd_tool_path: "htpasswd".to_string(),
            passwd_file_path: "/etc/nginx/erigon_htpasswd".to_string(),
            password_default_length: 15,
        }
    }
}

#[derive(Default, RuntimeDef)]
#[conf(ErigonConf)]
pub struct ErigonRuntime {
    erigon_username: Option<String>,
    erigon_password: Option<String>,
}

#[derive(Deserialize, Debug)]
struct BlockNumberRpcResponse {
    jsonrpc: String,
    id: u32,
    result: String,
}

impl Runtime for ErigonRuntime {
    fn deploy<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        let path = PathBuf::from(&ctx.conf.passwd_file_path);
        let erigon_addr = ctx.conf.erigon_http_addr.clone();
        let erigon_port = ctx.conf.erigon_http_port.clone();

        async move {
            let _ = touch(&path)
                .map_err(|_| {
                    error::Error::from_string(
                        "Wrong path to passwd_file_path: ".to_owned() + path.to_str().unwrap(),
                    )
                })
                .await?;
            verify_erigon_alive(&erigon_addr, &erigon_port)?;
            Ok(None)
        }
        .boxed_local()
    }

    fn start<'a>(&mut self, ctx: &mut Context<Self>) -> OutputResponse<'a> {
        // Generate user & password entry with passwd tool
        let username = format!("{}_{}", AUTH_ERIGON_USER_PREFIX, std::process::id());

        let rng = thread_rng();
        let password: String = rng
            .sample_iter(Alphanumeric)
            .map(char::from)
            .take(ctx.conf.password_default_length)
            .collect();
        self.erigon_username = Some(username.clone());
        self.erigon_password = Some(password.clone());

        let passwd_tool_path = ctx.conf.passwd_tool_path.clone();
        let passwd_file_path = ctx.conf.passwd_file_path.clone();
        async move {
            add_user_to_pass_file(&passwd_tool_path, &passwd_file_path, &username, &password)
                .map_err(|_| error::Error::from_string("Unable to add entry in passwd file"))?
                .await?;
            Ok(Some(serialize::json::json!({ "network": "mainnet" })))
        }
        .boxed_local()
    }

    fn stop<'a>(&mut self, ctx: &mut Context<Self>) -> EmptyResponse<'a> {
        //
        let passwd_tool_path = ctx.conf.passwd_tool_path.clone();
        let passwd_file_path = ctx.conf.passwd_file_path.clone();
        let erigon_username = self.erigon_username.as_ref().unwrap().clone();
        async move {
            remove_user_from_pass_file(&passwd_tool_path, &passwd_file_path, &erigon_username)
                .map_err(|_| error::Error::from_string("Unable to remove entry from passwd file"))?
                .await?;
            Ok(())
        }
        .boxed_local()
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
                    "user": &self.erigon_username,
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

fn add_user_to_pass_file(
    passwd_bin: &str,
    passwd_file: &str,
    username: &str,
    password: &str,
) -> std::io::Result<Child> {
    Command::new(passwd_bin)
        .arg("-b")
        .arg(passwd_file)
        .arg(username)
        .arg(password)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
}

fn remove_user_from_pass_file(
    passwd_bin: &str,
    passwd_file: &str,
    username: &str,
) -> std::io::Result<Child> {
    Command::new(passwd_bin)
        .arg("-D")
        .arg(passwd_file)
        .arg(username)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
}

// A simple implementation of `touch path` (ignores existing files)
async fn touch(path: &Path) -> io::Result<()> {
    OpenOptions::new()
        .create(true)
        .write(true)
        .open(path)
        .await
        .map(|_| ())
}

fn verify_erigon_alive(
    erigon_rpc_host: &str,
    erigon_rpc_port: &str,
) -> Result<BlockNumberRpcResponse, ya_runtime_sdk::error::Error> {
    let client = Client::new();
    client
        .post(format!("http://{}:{}", erigon_rpc_host, erigon_rpc_port))
        .header("Content-Type", "application/json")
        .body(
            serialize::json::json!({
                "id": 1,
                "method": "eth_blockNumber"
            })
            .to_string(),
        )
        .send()
        .unwrap()
        .json::<BlockNumberRpcResponse>()
        .map_err(|_| error::Error::from_string("Recieved RPC response has incorrect structure"))
}
