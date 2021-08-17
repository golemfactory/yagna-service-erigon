# Erigolem requestor

Requestor application for ordering Erigon nodes with a web interface.

This is the documentation of the requestor code.

Requestor code assumes there is a subnet with providers who:

* Have `ya-runtime-erigon` installed, 
* Emit an offer with this runtime.

Default name of this subnet is `erigon`. 


## Contents

* `run_erigon_service.py` - simple dev script that starts an erigon service and keeps it running until stopped
* `server` - http server + requestor code ([Quart](https://pgjones.gitlab.io/quart/) + [yapapi-service-manager](https://github.com/golemfactory/yapapi-service-manager))
* `server.Dockerfile`, `yagna_and_server_init.sh` - `server` running on [docker](https://docs.docker.com/)
* `client` - frontend code
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

All requests must contain a header `{'Authorization': 'Bearer [ETHEREUM_ADDRESS]'}`

    GET  /getInstances      - list of all instances created by the user (includes stopped instances)
    POST /createInstance    - create new instance, this requires "params" in body and also accepts optional "name"
    POST /stopInstance/<id> - stop instance with id <id>
