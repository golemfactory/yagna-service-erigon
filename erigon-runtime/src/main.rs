use futures::FutureExt;
use serde::{Deserialize, Serialize};
use structopt::StructOpt;
use ya_runtime_sdk::*;

#[derive(Default, RuntimeDef)]
//#[cli(ExampleCli)]
//#[conf(ExampleConf)]
pub struct ErigonRuntime;

impl Runtime for ErigonRuntime {
    const MODE: RuntimeMode = RuntimeMode::Command;

    fn deploy<'a>(&mut self, _: &mut Context<Self>) -> OutputResponse<'a> {
        async move { Ok("deploy".into()) }.boxed_local()
    }

    fn start<'a>(&mut self, _: &mut Context<Self>) -> OutputResponse<'a> {
        async move { Ok("start".into()) }.boxed_local()
    }

    fn stop<'a>(&mut self, _: &mut Context<Self>) -> EmptyResponse<'a> {
        println!("stop");
        async move { Ok(()) }.boxed_local()
    }

    fn run_command<'a>(
        &mut self,
        command: RunProcess,
        mode: RuntimeMode,
        _: &mut Context<Self>,
    ) -> ProcessIdResponse<'a> {
        println!("start_command: {:?} in {:?} mode", command, mode);
        async move { Ok(0) }.boxed_local()
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    ya_runtime_sdk::run::<ErigonRuntime>().await
}