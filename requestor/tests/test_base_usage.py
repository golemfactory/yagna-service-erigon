import pytest
import os
import requests
from time import sleep

BASE_URL = os.environ.get('BASE_URL')
if BASE_URL and '://' not in BASE_URL:
    BASE_URL = 'http://' + BASE_URL

USER_ID = 1231231231
ERIGON_NAME = 'test_erigon'


def run_request(method, endpoint, data={}):
    url = os.path.join(BASE_URL, endpoint)
    res = requests.request(method, url, json=data, headers={'Authorization': f'Bearer {USER_ID}'})
    return res.status_code, res.json()


def erigon_call_status(url, user, password):
    auth = requests.auth.HTTPBasicAuth(user, password)
    res = requests.post(url, auth=auth, headers={'content-type': 'application/json'})
    return res.status_code


@pytest.mark.skipif(not BASE_URL, reason="BASE_URL is required")
@pytest.mark.parametrize('network', ('kovan', 'rinkeby', 'ropsten', 'goerli'))
def test_api(network):
    #   1.  Create the instance
    init_params = {'network': network}
    status, data = run_request('POST', 'createInstance', {'params': init_params, 'name': ERIGON_NAME})
    assert status == 201
    erigon_id = data['id']
    assert (data['status'], data['id'], data['init_params'], data['name']) == \
           ('pending', erigon_id, init_params, ERIGON_NAME)
    assert 'created_at' in data

    #   2.  Wait for the instance to run
    for i in range(10):
        status, data = run_request('GET', 'getInstances')
        data = data[-1]
        assert status == 200
        if data['status'] == 'running':
            break
        sleep(3)
    else:
        assert False, 'Waited for running erigon too long'

    #   3.  Ensure we got what is expected
    assert data['id'] == erigon_id
    assert 'url' in data
    assert 'auth' in data
    assert 'password' in data['auth']
    assert 'user' in data['auth']
    #   This is the **imporiant** test, if we're running on the network we wanted
    assert data['network'] == network

    #   4.  Check if erigon is really working
    erigon_status = erigon_call_status(data['url'], data['auth']['user'], data['auth']['password'])

    #   TODO: this should be always 200, but when a provider just starts with the new network it is 502
    #         (we plan to address this somehow, but don't know how)
    assert erigon_status in (200, 502)

    #   5.  Stop the instance
    status, data = run_request('POST', f'stopInstance/{erigon_id}')
    assert status == 200

    status, data = run_request('GET', 'getInstances')
    assert status == 200
    data = data[-1]
    assert (data['status'], data['id'], data['init_params'], data['name']) == \
           ('stopped', erigon_id, init_params, ERIGON_NAME)
    assert 'created_at' in data
    assert 'stopped_at' in data
