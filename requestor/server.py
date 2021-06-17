from quart import Quart, request
from quart_cors import cors
from service_manager import ServiceManager, ServiceWrapper
import erigon_services
from collections import defaultdict
import json
import os
from datetime import datetime

app = Quart(__name__)
cors(app)


app.user_erigons = defaultdict(dict)


ERIGON_CLS = getattr(erigon_services, os.environ.get('ERIGON_CLASS', 'Erigon'))


class ErigonServiceWrapper(ServiceWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = None
        self._created_at = datetime.utcnow()
        self._stopped_at = None

    def stop(self):
        super().stop()
        if self._stopped_at is None:
            self._stopped_at = datetime.utcnow()

    def api_repr(self):
        if self.stopped:
            status = 'stopped'
        elif not self.started:
            status = 'pending'
        else:
            if self.service.url is None:
                status = 'starting'
            else:
                status = 'running'

        data = {
            'id': self.id,
            'status': status,
            'name': self.name,
            'init_params': self.start_args[0],
            'created_at': self._created_at.isoformat(),
        }
        if status == 'running':
            data['url'] = self.service.url
            data['auth'] = self.service.auth
            data['network'] = self.service.network
        elif status == 'stopped':
            data['stopped_at'] = self._stopped_at.isoformat()

        return data


class UserDataMissing(Exception):
    pass


def get_config():
    cfg = {
        #   NOTE: budget == 10 is not enough to make it run for long
        'budget': 10,
        'subnet_tag': os.environ.get('SUBNET_TAG', 'erigon'),
    }
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
    data = [erigon.api_repr() for erigon in erigons]
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
    erigon = app.service_manager.create_service(ERIGON_CLS, [init_params], ErigonServiceWrapper)
    erigon.name = request_data.get('name', f'erigon_{erigon.id}')

    #   Save the data
    user_id = await get_user_id()
    app.user_erigons[user_id][erigon.id] = erigon

    return erigon.api_repr(), 201


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

    erigon.stop()

    return erigon.api_repr(), 200


@app.errorhandler(UserDataMissing)
def handle_bad_request(e):
    return 'All requests require {"user_id": "anything"} body', 400


if __name__ == '__main__':
    #   TODO: we haven't decided yet how we'll be serving the app
    #         (e.g. is it possible to use more than one gunicorn woker?)
    #         so it runs just this way as a prototype
    app.run(host='0.0.0.0')
