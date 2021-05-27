import httpx
import pytest
import os
import asyncio

BASE_URL = os.environ.get('BASE_URL')
if BASE_URL and '://' not in BASE_URL:
    BASE_URL = 'http://' + BASE_URL


def create_request(method, endpoint, user_id):
    url = os.path.join(BASE_URL, endpoint)
    user_id_data = {'user_id': user_id}

    req = httpx.Request(method, url, json=user_id_data)

    return req


@pytest.mark.asyncio
@pytest.mark.skipif(not BASE_URL, reason="BASE_URL is required")
async def test_api():
    async with httpx.AsyncClient() as client:
        requests = []
        for i in range(3):
            req = create_request('POST', 'createInstance', i)
            requests.append(client.send(req))

        await asyncio.gather(*requests)
