from quart import Quart, request
from quart_cors import cors
from yapapi_service_manager import ServiceManager
from collections import defaultdict
import json

from .erigon_service import Erigon
from .erigon_service_wrapper import ErigonServiceWrapper

app = Quart(__name__)
cors(app)


app.user_erigons = defaultdict(dict)


class UserDataMissing(Exception):
    pass


@app.before_serving
async def start_service_manager():
    app.service_manager = ServiceManager(app.yapapi_executor_config)


@app.after_serving
async def close_service_manager():
    await app.service_manager.close()


def get_user_id():
    try:
        auth = request.headers['Authorization']
    except KeyError:
        raise UserDataMissing('Missing authorization header')

    if auth.startswith("Bearer "):
        token = auth[7:]
    else:
        raise UserDataMissing('Authorization header should start with "Bearer "')

    if len(token) != 42:
        raise UserDataMissing('Token is expected to be exactly 42 characters long')

    return token


@app.route('/getInstances', methods=['GET'])
async def get_instances():
    user_id = get_user_id()
    erigons = list(app.user_erigons[user_id].values())
    data = [erigon.api_repr() for erigon in erigons]
    return json.dumps(data), 200


@app.route('/createInstance', methods=['POST'])
async def create_instance():
    user_id = get_user_id()

    #   Get init params from request
    request_data = await request.json
    try:
        init_params = request_data['params']
    except KeyError:
        return "'params' key is required", 400

    if type(init_params) is not dict:
        return "'params' should be an object", 400

    #   Initialize erigon
    erigon = app.service_manager.create_service(Erigon, [init_params], ErigonServiceWrapper)
    erigon.name = request_data.get('name', f'erigon_{erigon.id}')

    #   Save the data
    app.user_erigons[user_id][erigon.id] = erigon

    return erigon.api_repr(), 201


@app.route('/stopInstance/<erigon_id>', methods=['POST'])
async def stop_instance(erigon_id):
    user_id = get_user_id()
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
    return {'msg': str(e)}, 400
