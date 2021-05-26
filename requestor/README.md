# run requestor server

    docker build . -f server.Dockerfile -t erigon-server

    #   Run on devnet with a mocked Erigon
    docker run -p 5000:5000 -e ERIGON_CLASS=PseudoErigon -e SUBNET_TAG=devnet-beta.1 erigon-server 

    #   or run with a real Erigon, assuming there is some subnet that supports it
    docker run -p 5000:5000 -e SUBNET_TAG=some_subnet_with_erigon erigon-server

# test requestor server

    #   Check if the server is running (this returns 400 because of missing user_id)
    curl http://localhost:5000/getInstances

    #   Prepare testing image
    docker build . -f test.Dockerfile -t erigon-server-test
    
    #   Run a simple test with only one provider required
    docker run --network=host -e BASE_URL=localhost:5000 erigon-server-test tests/test_base_usage.py
    
    #   Run full tests that assume at least 3 providers
    docker run --network=host -e BASE_URL=localhost:5000 erigon-server-test
