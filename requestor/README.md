# Erigolem requestor

Requestor application for ordering Erigon nodes with a web interface.

This is the documentation of the requestor code.

Requestor code assumes there is a subnet with providers who:

* Have `ya-runtime-erigon` installed, 
* Emit an offer with this runtime.

Default name of this subnet is `erigon`. 


## Contents

* `server` - http server + requestor code ([Quart](https://pgjones.gitlab.io/quart/) + [yapapi-service-manager](https://github.com/golemfactory/yapapi-service-manager))
* `server.Dockerfile`, `yagna_and_server_init.sh` - `server` running on [docker](https://docs.docker.com/)
* `tests`, `tests.Dockerfile` - test if the server works properly

## Run requestor server
    
    #   NOTE: consider --no-cache switch because layer with yapapi pull
    #   might be cached and you might want a fresh yapapi pull
    docker build . -f server.Dockerfile -t erigon-server
    
    #   Run the "production"-like environment (the default subnet tag is 'erigon')
    docker run -p 5000:5000 erigon-server
    
    #   Run on some other subnet
    docker run -p 5000:5000 -e SUBNET_TAG=some_subnet_with_erigon erigon-server

## Stop requestor server gracefully

    docker stop <SERVER-CONTAINER-NAME>

## Test requestor server

    #   Check if the server is running (this returns 400)
    curl http://localhost:5000/getInstances

    #   Prepare testing image
    docker build . -f test.Dockerfile -t erigon-server-test
    
    #   Run a simple test with only one provider required
    docker run --network=host -e BASE_URL=localhost:5000 erigon-server-test
    
    #   Run full tests that assume at least 3 providers
    docker run --network=host -e BASE_URL=localhost:5000 -e PROVIDER_CNT=3 erigon-server-test

## Use requestor server

### Endpoints

All requests must contain a header `{'Authorization': 'Bearer [ETHEREUM_ADDRESS]'}`

    GET  /getInstances      - list of all instances created by the user (includes stopped instances)
    POST /createInstance    - create new instance, this requires "params" in body and also accepts optional "name"
    POST /stopInstance/<id> - stop instance with id <id>

### Command-line interface

All further examples assume having a Python environment set up and active. It needs to be done once before using the CLI.
```shell
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

You can use CLI to interact with the requestor server. First, generate a `keystore.json` file and save it under this (requestor) directory. You can export from yagna or use [vanity-eth](https://vanity-eth.tk/). Then you can list, create and stop erigon instances with CLI:
```shell
$ ./erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> list 
[]
$ ./erigolem_cli.py --keystore ./keystore.json --password <PASSWORD>  create '{"name": "My Node", "params": {"network": "goerli"}}'
{'created_at': '2022-03-07T15:35:59.355692', 'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'init_params': {'network': 'goerli'}, 'name': 'My Node', 'status': 'pending'}
$ ./erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> list
[{'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'status': 'running', 'name': 'My Node', 'init_params': {'network': 'goerli'}, 'created_at': '2022-03-07T15:35:59.355692', 'url': 'https://0.erigon.golem.network:8545', 'auth': {'password': '4P0o087q43FlmoP', 'user': 'erigolem'}, 'network': 'goerli'}]
$ ./erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> stop a2303ae2c2de4a83a86a8fa69cb9b303
{'auth': {'password': '4P0o087q43FlmoP', 'user': 'erigolem'}, 'created_at': '2022-03-07T15:35:59.355692', 'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'init_params': {'network': 'goerli'}, 'name': 'My Node', 'network': 'goerli', 'status': 'running', 'url': 'https://0.erigon.golem.network:8545'}
$ ./erigolem_cli.py --keystore ./keystore.json --password <PASSWORD> list 
[{'id': 'a2303ae2c2de4a83a86a8fa69cb9b303', 'status': 'stopped', 'name': 'My Node', 'init_params': {'network': 'goerli'}, 'created_at': '2022-03-07T15:35:59.355692', 'stopped_at': '2022-03-07T15:36:31.939827'}]
```
To see all commands and parameters run `./erigolem_cli.py --help`

### Network checker

CLI has an additional functionality – _network checker_. It is a service that keeps the network busy by maintaining a fixed number of active providers (`--num-instances`). Running nodes are periodically (`--check-interval-sec`) checked. These who take too long to start (`--pending-timeout-sec`) or fail to respond correctly to web3 requests are restarted.  

Example usage:

```shell
$ ./erigolem_cli.py --password <PASSWORD> --log-level DEBUG net-check --num-instances 3 --check-interval-sec 20
Starting network check...
debug: Starting new HTTP connection (1): localhost:5000
debug: http://localhost:5000 "GET /getInstances HTTP/1.1" 200 630
Active instances: 0 / 3
Creating 3 new instances...
Creating new instance...
debug: Starting new HTTP connection (1): localhost:5000
Creating new instance...
Creating new instance...
Finished creating new instances
debug: Starting new HTTP connection (1): localhost:5000
debug: Starting new HTTP connection (1): localhost:5000
Network check done
debug: http://localhost:5000 "POST /createInstance HTTP/1.1" 201 154
Instance d886d884f47c47d9aef05aa9fa984216 created
debug: http://localhost:5000 "POST /createInstance HTTP/1.1" 201 154
debug: http://localhost:5000 "POST /createInstance HTTP/1.1" 201 154
Instance 2bce0c4a0072440f9e6e7a6373c0d1e1 created
Instance fcddd90e058c4e569183424173407092 created
...
Starting network check...
debug: Resetting dropped connection: localhost
debug: http://localhost:5000 "GET /getInstances HTTP/1.1" 200 1677
Active instances: 3 / 3
Network check done
debug: Making request. Method: eth_blockNumber
debug: Making request HTTP. URI: https://3.erigon.golem.network:8545, Method: eth_blockNumber
debug: Making request. Method: eth_blockNumber
debug: Making request. Method: eth_blockNumber
debug: Making request HTTP. URI: https://1.erigon.golem.network:8545, Method: eth_blockNumber
debug: Making request HTTP. URI: https://0.erigon.golem.network:8545, Method: eth_blockNumber
debug: Starting new HTTPS connection (1): 0.erigon.golem.network:8545
debug: https://1.erigon.golem.network:8545 "POST / HTTP/1.1" 200 64
debug: Getting response HTTP. URI: https://1.erigon.golem.network:8545, Method: eth_blockNumber, Response: {'jsonrpc': '2.0', 'id': 0, 'result': '0x0'}
debug: Block: 0
debug: https://0.erigon.golem.network:8545 "POST / HTTP/1.1" 200 64
debug: Getting response HTTP. URI: https://0.erigon.golem.network:8545, Method: eth_blockNumber, Response: {'jsonrpc': '2.0', 'id': 0, 'result': '0x0'}
debug: Block: 0
debug: https://3.erigon.golem.network:8545 "POST / HTTP/1.1" 200 64
debug: Getting response HTTP. URI: https://3.erigon.golem.network:8545, Method: eth_blockNumber, Response: {'jsonrpc': '2.0', 'id': 0, 'result': '0x0'}
debug: Block: 0
...
^C
Shutting down network checker...
debug: Resetting dropped connection: localhost
debug: http://localhost:5000 "GET /getInstances HTTP/1.1" 200 1677
Stopping instance d886d884f47c47d9aef05aa9fa984216 ...
debug: Resetting dropped connection: localhost
Stopping instance fcddd90e058c4e569183424173407092 ...
debug: Resetting dropped connection: localhost
Stopping instance a3cb45bc85ab4db4885c3b299ea01a1d ...
debug: Resetting dropped connection: localhost
debug: http://localhost:5000 "POST /stopInstance/fcddd90e058c4e569183424173407092 HTTP/1.1" 200 273
Instance fcddd90e058c4e569183424173407092 stopped.
debug: http://localhost:5000 "POST /stopInstance/a3cb45bc85ab4db4885c3b299ea01a1d HTTP/1.1" 200 273
Instance a3cb45bc85ab4db4885c3b299ea01a1d stopped.
debug: http://localhost:5000 "POST /stopInstance/d886d884f47c47d9aef05aa9fa984216 HTTP/1.1" 200 273
Instance d886d884f47c47d9aef05aa9fa984216 stopped.
Network checker shutdown complete
```
