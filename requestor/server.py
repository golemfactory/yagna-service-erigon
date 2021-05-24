from quart import Quart, request
from yagna_erigon_manager import YagnaErigonManager
from collections import defaultdict
import json

app = Quart(__name__)

yem = YagnaErigonManager()

user_erigons = defaultdict(list)


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


@app.after_serving
async def close_yagna_erigon_manager():
    await yem.close()

if __name__ == '__main__':
    app.run()
