from quart import Quart, request
from quart_cors import cors
from service_manager import ServiceManager
import erigon_services
from collections import defaultdict
from dataclasses import dataclass
import json
import os

app = Quart(__name__)
cors(app)


app.user_erigons = defaultdict(dict)


ERIGON_CLS = getattr(erigon_services, os.environ.get('ERIGON_CLASS', 'Erigon'))


@dataclass
class ErigonData():
    erigon: ERIGON_CLS
    name: str
    init_params: dict

    def api_repr(self):
        erigon = self.erigon

        if erigon.stopped:
            status = 'stopped'
        elif not erigon.started:
            status = 'pending'
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
            data['network'] = erigon.service.network

        data['name'] = self.name
        data['init_params'] = self.init_params

        return data


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


@app.route('/getInstances', methods=['POST'])
async def get_instances():
    user_id = await get_user_id()
    erigons = list(app.user_erigons[user_id].values())
    data = [erigon_data.api_repr() for erigon_data in erigons]
    return json.dumps(data), 200


@app.route('/createInstance', methods=['POST'])
async def create_instance():
    #   Get init params from request
    request_data = await request.json
    try:
        init_params = request_data['params']
    except KeyError:
        return "'params' key is required", 400

    if type(init_params) is not dict:
        return "'params' should be an object", 400

    #   Initialize erigon
    erigon = app.service_manager.create_service(ERIGON_CLS, [init_params])

    #   Save the data
    name = request_data.get('name', f'erigon_{erigon.id}')
    erigon_data = ErigonData(erigon, name, init_params)
    user_id = await get_user_id()
    app.user_erigons[user_id][erigon.id] = erigon_data

    return erigon_data.api_repr(), 201


@app.route('/stopInstance/<erigon_id>', methods=['POST'])
async def stop_instance(erigon_id):
    user_id = await get_user_id()
    try:
        this_user_erigons = app.user_erigons[user_id]
    except KeyError:
        return 'Invalid user_id', 403

    try:
        erigon_data = this_user_erigons[erigon_id]
    except KeyError:
        return 'Invalid erigon_id', 404

    await erigon_data.erigon.stop()

    return erigon_data.api_repr(), 200


@app.errorhandler(UserDataMissing)
def handle_bad_request(e):
    return 'All requests require {"user_id": "anything"} body', 400


if __name__ == '__main__':
    #   TODO: we haven't decided yet how we'll be serving the app
    #         (e.g. is it possible to use more than one gunicorn woker?)
    #         so it runs just this way as a prototype
    app.run(host='0.0.0.0')
