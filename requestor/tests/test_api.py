import pytest
import os
import requests

BASE_URL = os.environ.get('BASE_URL')
if BASE_URL and '://' not in BASE_URL:
    BASE_URL = 'http://' + BASE_URL

USER_ID = 123


def run_request(method, endpoint):
    user_id_data = {'user_id': USER_ID}
    url = os.path.join(BASE_URL, endpoint)
    res = requests.request(method, url, json=user_id_data)
    return res.status_code, res.json()


@pytest.mark.skipif(not BASE_URL, reason="BASE_URL is required")
def test_api():
    assert run_request('GET', 'getInstances') == (200, [])

    status, data = run_request('POST', 'createInstance')
    assert status == 201
    assert data['status'] == 'starting'
    assert data['url'] is None
    erigon_id = data['id']

    assert run_request('GET', 'getInstances') == (200, [data])
