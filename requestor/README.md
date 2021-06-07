# run requestor server
    
    #   NOTE: consider --no-cache switch if you built this recently because layer with 
    #   yapapi pulling might be cached and you might want a fresh yapapi pull
    docker build . -f server.Dockerfile -t erigon-server
    
    #   Run the "production"-like environment (the default subnet tag is 'erigon')
    docker run -p 5000:5000 erigon-server

    #   Run on devnet with a mocked Erigon
    docker run -p 5000:5000 -e ERIGON_CLASS=PseudoErigon -e SUBNET_TAG=devnet-beta.2 erigon-server 
    
    #   Run with a real Erigon, on some other subnet
    docker run -p 5000:5000 -e SUBNET_TAG=some_subnet_with_erigon erigon-server

# stop requestor server gracefully

    docker exec -it <SERVER-CONTAINER-NAME> pkill python

# test requestor server

    #   Check if the server is running (this returns 405)
    curl http://localhost:5000/getInstances

    #   Prepare testing image
    docker build . -f test.Dockerfile -t erigon-server-test
    
    #   Run a simple test with only one provider required
    docker run --network=host -e BASE_URL=localhost:5000 erigon-server-test
    
    #   Run full tests that assume at least 3 providers
    docker run --network=host -e BASE_URL=localhost:5000 -e PROVIDER_CNT=3 erigon-server-test

# use requestor server

All requests except static file request must contain a JSON body with 'user\_id': 'the\_thing\_from\_metamask'.

    POST /getInstances      - list of all instances created by the user (includes stopped instances)
    POST /createInstance    - create new instance, this requires "params" along the "user_id" in body and also accepts optional "name"
    POST /stopInstance/<id> - stop instance with id <id>
