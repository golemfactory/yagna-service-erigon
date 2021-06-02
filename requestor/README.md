# run requestor server
    
    #   NOTE: consider --no-cache switch if you built this recently because layer with 
    #   yapapi pulling might be cached and you might want a fresh yapapi pull
    docker build . -f server.Dockerfile -t erigon-server

    #   Run on devnet with a mocked Erigon
    docker run -p 5000:5000 -e ERIGON_CLASS=PseudoErigon -e SUBNET_TAG=devnet-beta.1 erigon-server 

    #   or run with a real Erigon, assuming there is some subnet that supports it
    docker run -p 5000:5000 -e SUBNET_TAG=some_subnet_with_erigon erigon-server

# stop requestor server gracefully

    docker exec -it <SERVER-CONTAINER-NAME> pkill python

# test requestor server

NOTE: tests might *sometimes* fail with a slow/unreliable provider. Please repeat : )

    #   Check if the server is running (this returns 400 because of missing user_id)
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
    POST /createInstance    - create new instance (this *should* use some config data from body, but 
                              currently everything except 'user_id' is ignored)
    POST /stopInstance/<id> - stop instance with id <id>
    GET  /static/<path>     - return a file from 'static' directory, on a given path
                              (NOTE: this probably should be done somewhere else (nginx?) in the final version)
                              e.g GET /static/index.html 
