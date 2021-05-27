from quart import Quart, request, send_from_directory
from service_manager import YagnaErigonManager, services
from collections import defaultdict
import json
import asyncio
import os

app = Quart(__name__)


user_erigons = defaultdict(dict)

yem = None


class UserDataMissing(Exception):
    pass


async def create_yem():
    global yem
    yem = YagnaErigonManager(get_config())


def get_config():
    cfg = {}
    subnet_tag = os.environ.get('SUBNET_TAG', '')
    if subnet_tag:
        cfg['subnet_tag'] = subnet_tag
    return cfg


def erigon_cls():
    erigon_cls_name = os.environ.get('ERIGON_CLASS', 'Erigon')
    erigon_cls = getattr(services, erigon_cls_name)
    return erigon_cls


@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    loop.create_task(create_yem())

    #   This is called only to validate the env (or die now)
    erigon_cls()


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

    data = {
        'id': erigon.id,
        'status': status,
    }

    if status == 'running':
        data['url'] = erigon.runtime_state.url
        data['auth'] = erigon.runtime_state.auth
    return data


@app.route('/getInstances', methods=['GET'])
async def get_instances():
    user_id = await get_user_id()
    erigons = list(user_erigons[user_id].values())
    data = [erigon_data(erigon) for erigon in erigons]
    return json.dumps(data), 200


@app.route('/createInstance', methods=['POST'])
async def create_instance():
    user_id = await get_user_id()
    erigon = yem.create_erigon(erigon_cls())
    user_erigons[user_id][erigon.id] = erigon
    return erigon_data(erigon), 201


@app.route('/stopInstance/<erigon_id>', methods=['POST'])
async def stop_instance(erigon_id):
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


@app.route('/static/<path:filename>', methods=['GET'])
async def static_file(filename):
    return send_from_directory('static', filename)


@app.errorhandler(UserDataMissing)
def handle_bad_request(e):
    return 'All requests require {"user_id": "anything"} body', 400


if __name__ == '__main__':
    #   TODO: we haven't decided yet how we'll be serving the app
    #         (e.g. is it possible to use more than one gunicorn woker?)
    #         so it runs just this way as a prototype
    app.run(host='0.0.0.0')
