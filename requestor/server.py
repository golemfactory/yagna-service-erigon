from quart import Quart, request
from yagna_erigon_manager import YagnaErigonManager
from collections import defaultdict
import json
import asyncio
import services

app = Quart(__name__)


user_erigons = defaultdict(dict)

yem = None


class UserDataMissing(Exception):
    pass


async def create_yem():
    global yem
    yem = YagnaErigonManager()


@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    loop.create_task(create_yem())


@app.after_serving
async def close_yagna_erigon_manager():
    await yem.close()


async def get_user_id():
    try:
        data = await request.json
        return data['user_id']
    except Exception:
        raise UserDataMissing


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
    erigons = list(user_erigons[user_id].values())
    data = [erigon_data(erigon) for erigon in erigons]
    return json.dumps(data), 200


@app.route('/createInstance', methods=['POST'])
async def create_instance():
    user_id = await get_user_id()
    erigon = yem.create_erigon(services.Erigon)
    user_erigons[user_id][erigon.id] = erigon
    return erigon_data(erigon), 201


@app.route('/stopInstance/<erigon_id>', methods=['POST'])
async def sop_instance(erigon_id):
    user_id = await get_user_id()
    try:
        this_user_erigons = user_erigons[user_id]
    except KeyError:
        return 'Invalid user_id', 401

    try:
        erigon = this_user_erigons[erigon_id]
    except KeyError:
        return 'Invalid erigon_id', 404

    await erigon.stop()
    return erigon_data(erigon), 200


@app.errorhandler(UserDataMissing)
def handle_bad_request(e):
    return 'All requests require {"user_id": "anything"} body', 400


if __name__ == '__main__':
    #   TODO: we haven't decided yet how we'll be serving the app
    #         (e.g. is it possible to use more than one gunicorn woker?)
    #         so it runs just this way as a prototype
    app.run(host='0.0.0.0')
