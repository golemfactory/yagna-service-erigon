# Erigolem
Erigon node as a Golem service

The purpose of this example is to demonstrate building a Golem service using a dedicated, self-contained runtime. It features an Ethereum network client, Erigon (f.k.a. Turbo-geth) started on provider nodes on user's demand. Interaction with the service, once it's running and its location and credentials have been passed to the requestor, is *not* facilitated by Golem though.

---

The application consist of three major components:

1. **User interface** (`client/`)  
   A browser-based interface written in TypeScript using [React](https://reactjs.org/). It allows the end user to interact with the application, i.e. start an Erigon node after authenticating with their [Metamask](https://metamask.io/) wallet, and later manage their node(s).
2. **Requestor server** (`requestor/`)  
   A Python application developed using [Quart](https://pgjones.gitlab.io/quart/) and [yapapi-service-manager](https://github.com/golemfactory/yapapi-service-manager). It acts both as an HTTP server (handling requests from the user interface), and as a requestor agent (submitting tasks to the Golem network).
3. **Erigon runtime** (`ya-runtime-erigon/`)  
    A dedicated, self-contained runtime created with [ya-runtime-sdk](https://github.com/golemfactory/ya-runtime-sdk). It is a Rust binary wrapping [Erigon](https://github.com/ledgerwatch/erigon) service itself so that it can be orchestrated by yagna daemon. The runtime also controls the access to the service by managing [Nginx](https://www.nginx.com/) configuration.

---

To use the application locally, run `docker-compose up` and open [http://localhost:8000](). You can provide your own subnet by setting up the `SUBNET_TAG` environment variable.

Instructions how to run client and e2e tests are [here](https://github.com/golemfactory/yagna-service-erigon/blob/master/client/README.md).
Instructions how to run and test the requestor server are [here](https://github.com/golemfactory/yagna-service-erigon/blob/master/requestor/README.md).

Full project documentation can be found in the [Golem handbook](https://handbook.golem.network/requestor-tutorials/service-development/service-example-2-managed-erigon).

---
 
You can use CLI to interact with the requestor server. First, generate a `keystore.json` file. You can export from yagna or use [vanity-eth](https://vanity-eth.tk/). Then you can list, create and stop erigon instances:
```shell
$ python requestor/erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> list 
[]
$ python requestor/erigolem_cli.py --keystore ./keystore.json --password <PASSWORD>  create '{"name": "My Node", "params": {"network": "goerli"}}'
{'created_at': '2022-03-07T15:35:59.355692', 'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'init_params': {'network': 'goerli'}, 'name': 'My Node', 'status': 'pending'}
$ python requestor/erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> list
[{'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'status': 'running', 'name': 'My Node', 'init_params': {'network': 'goerli'}, 'created_at': '2022-03-07T15:35:59.355692', 'url': 'https://0.erigon.golem.network:8545', 'auth': {'password': '4P0o087q43FlmoP', 'user': 'erigolem'}, 'network': 'goerli'}]
$ python requestor/erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> stop a2303ae2c2de4a83a86a8fa69cb9b303
{'auth': {'password': '4P0o087q43FlmoP', 'user': 'erigolem'}, 'created_at': '2022-03-07T15:35:59.355692', 'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'init_params': {'network': 'goerli'}, 'name': 'My Node', 'network': 'goerli', 'status': 'running', 'url': 'https://0.erigon.golem.network:8545'}
$ python requestor/erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> list 
[{'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'status': 'stopped', 'name': 'My Node', 'init_params': {'network': 'goerli'}, 'created_at': '2022-03-07T15:35:59.355692', 'stopped_at': '2022-03-07T15:36:31.939827'}]
```
