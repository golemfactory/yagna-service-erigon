import httpx
import pytest
import os
import asyncio

BASE_URL = os.environ.get('BASE_URL')
if BASE_URL and '://' not in BASE_URL:
    BASE_URL = 'http://' + BASE_URL

PROVIDER_CNT = int(os.environ.get('PROVIDER_CNT', '1'))


def create_request(method, endpoint, user_id, data={}):
    url = os.path.join(BASE_URL, endpoint)
    req = httpx.Request(method, url, json=data, headers={'Authorization': f'Bearer {user_id}'})

    return req


def instance_data(user_id):
    return {
        'params': {
            'network': 'goerli',
        },
        'name': f'erigon_created_by_{user_id}',
    }


async def check_data(client, not_started_ids, user_id):
    req = create_request('GET', 'getInstances', user_id)
    res = await client.send(req)
    assert res.status_code == 200
    data = res.json()[-1]

    if data['status'] == 'running':
        print(f"STARTED FOR USER {user_id}")
        if user_id in not_started_ids:
            not_started_ids.remove(user_id)
    else:
        print(f"NOT STARTED YET FOR USER {user_id}")


async def get_any_erigon(client, user_id):
    req = create_request('GET', 'getInstances', user_id)
    res = await client.send(req)
    assert res.status_code == 200
    return res.json()[-1]


@pytest.mark.asyncio
@pytest.mark.skipif(not BASE_URL, reason="BASE_URL is required")
@pytest.mark.skipif(PROVIDER_CNT < 3, reason="Not enough providers")
async def test_api():
    user_ids = list(range(10**10, 10**10 + 3))

    #   1.  Send many requests at the same time
    async with httpx.AsyncClient() as client:
        requests = []
        for user_id in user_ids:
            req = create_request('POST', 'createInstance', user_id, instance_data(user_id))

            requests.append(client.send(req))

        await asyncio.gather(*requests)

    #   2.  Wait until everything started
    not_started_ids = user_ids.copy()
    async with httpx.AsyncClient() as client:
        for i in range(0, 10):
            if not not_started_ids:
                print("ALL STARTED")
                break

            requests = []
            for user_id in not_started_ids:
                requests.append(check_data(client, not_started_ids, user_id))

            await asyncio.gather(*requests)
            await asyncio.sleep(3)
        assert not not_started_ids

    #   3.  Stop everything
    async with httpx.AsyncClient() as client:
        requests = []
        for user_id in user_ids:
            erigon = await get_any_erigon(client, user_id)
            erigon_id = erigon['id']
            req = create_request('POST', f'stopInstance/{erigon_id}', user_id)

            requests.append(client.send(req))

        await asyncio.gather(*requests)

    #   4.  Check if everything is stopped
    async with httpx.AsyncClient() as client:
        for user_id in user_ids:
            erigon = await get_any_erigon(client, user_id)
            assert erigon['status'] == 'stopped'
