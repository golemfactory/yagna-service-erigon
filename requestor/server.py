from quart import Quart, request
from quart_cors import cors
from service_manager import ServiceManager
import erigon_services
from collections import defaultdict
import json
import os

app = Quart(__name__)
cors(app)


app.user_erigons = defaultdict(dict)


ERIGON_CLS = getattr(erigon_services, os.environ.get('ERIGON_CLASS', 'Erigon'))


class UserDataMissing(Exception):
    pass


def get_config():
    cfg = {}
    subnet_tag = os.environ.get('SUBNET_TAG', '')
    if subnet_tag:
        cfg['subnet_tag'] = subnet_tag
    return cfg


@app.before_serving
async def startup():
    app.service_manager = ServiceManager(get_config())


@app.after_serving
async def close_service_manager():
    await app.service_manager.close()


async def get_user_id():
    data = await request.json
    try:
        return data['user_id']
    except KeyError:
        raise UserDataMissing


def erigon_data(erigon):
    if not erigon.started:
        status = 'pending'
    elif erigon.stopped:
        status = 'stopped'
    else:
        if erigon.service.url is None:
            status = 'starting'
        else:
            status = 'running'

    data = {
        'id': erigon.id,
        'status': status,
    }

    if status == 'running':
        data['url'] = erigon.service.url
        data['auth'] = erigon.service.auth
    return data


@app.route('/getInstances', methods=['POST'])
async def get_instances():
    user_id = await get_user_id()
    erigons = list(app.user_erigons[user_id].values())
    data = [erigon_data(erigon) for erigon in erigons]
    return json.dumps(data), 200


@app.route('/createInstance', methods=['POST'])
async def create_instance():
    user_id = await get_user_id()
    erigon = app.service_manager.create_service(ERIGON_CLS)
    app.user_erigons[user_id][erigon.id] = erigon
    return erigon_data(erigon), 201


@app.route('/stopInstance/<erigon_id>', methods=['POST'])
async def stop_instance(erigon_id):
    user_id = await get_user_id()
    try:
        this_user_erigons = app.user_erigons[user_id]
    except KeyError:
        return 'Invalid user_id', 403

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
