from quart import Quart, request
from yagna_erigon_manager import YagnaErigonManager
from collections import defaultdict
import json
import asyncio

app = Quart(__name__)


user_erigons = defaultdict(list)

yem = None


async def create_yem():
    global yem
    yem = YagnaErigonManager()

@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    main_task = loop.create_task(create_yem())

@app.after_serving
async def close_yagna_erigon_manager():
    await yem.close()

async def get_user_id():
    data = await request.json
    return data['user_id']


def erigon_data(erigon):
    if erigon.stopped:
        status = 'stopped'
    elif erigon.started:
        status = 'running'
    else:
        status = 'starting'

    return {
        'id': erigon.id,
        'url': erigon.runtime_state.url,
        'status': status,
    }


@app.route('/getInstances', methods=['GET'])
async def get_instances():
    user_id = await get_user_id()
    erigons = user_erigons[user_id]
    data = [erigon_data(erigon) for erigon in erigons]
    return json.dumps(data), 200


@app.route('/createInstance', methods=['POST'])
async def create_instance():
    user_id = await get_user_id()
    erigon = yem.create_erigon()
    user_erigons[user_id].append(erigon)
    return erigon_data(erigon), 201


if __name__ == '__main__':
    app.run()
