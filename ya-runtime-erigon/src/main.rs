use futures::FutureExt;
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use serde::{Deserialize, Serialize};
use std::process::Stdio;
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

impl Runtime for ErigonRuntime {
    fn deploy<'a>(&mut self, _ctx: &mut Context<Self>) -> OutputResponse<'a> {
        async move { Ok(None) }.boxed_local()
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

        let _ = generate_password_file(
            &ctx.conf.passwd_tool_path,
            &ctx.conf.passwd_file_path,
            &username,
            &password,
        )
        .expect("Unable to create passwd file");
        self.erigon_username = Some(username);
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

fn generate_password_file(
    passwd_bin: &String,
    passwd_file: &String,
    username: &String,
    password: &String,
) -> std::io::Result<Child> {
    Command::new(passwd_bin)
        .arg("-cb")
        .arg(passwd_file)
        .arg(username)
        .arg(password)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
}
