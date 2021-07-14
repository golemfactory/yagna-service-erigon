from collections import defaultdict
import json
from typing import TYPE_CHECKING

from quart import Quart, request, abort, jsonify
from quart_cors import cors
from yapapi_service_manager import ServiceManager
from web3 import Web3

from .erigon_service import Erigon
from .erigon_service_wrapper import ErigonServiceWrapper

if TYPE_CHECKING:
    from typing import Optional, Mapping
    from yapapi_service_manager import ServiceWrapper  # pylint: disable=C0412


class App(Quart):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.user_erigons: 'Mapping[str, Mapping[str, ServiceWrapper]]' = defaultdict(dict)
        self.service_manager: 'Optional[ServiceManager]' = None
        self.yapapi_executor_config: 'Optional[dict]' = None


app = App()
cors(app)


@app.before_serving
async def start_service_manager():
    app.service_manager = ServiceManager(app.yapapi_executor_config)


@app.after_serving
async def close_service_manager():
    await app.service_manager.close()


def abort_json_400(msg):
    data = {'msg': msg}
    response = jsonify(data)
    response.status_code = 400
    abort(response)


def get_user_id():
    try:
        auth = request.headers['Authorization']
    except KeyError:
        abort_json_400('Missing authorization header')

    if auth.startswith("Bearer "):
        token = auth[7:]
    else:
        abort_json_400('Authorization header should start with "Bearer "')

    if not Web3.isAddress(token):
        abort_json_400(f'{token} is not a correct address')

    return token


@app.route('/getInstances', methods=['GET'])
async def get_instances():
    user_id = get_user_id()
    erigons = app.user_erigons[user_id].values()
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

    if not isinstance(init_params, dict):
        return "'params' should be an object", 400

    #   Initialize erigon
    erigon = app.service_manager.create_service(Erigon, (init_params,), ErigonServiceWrapper)
    erigon.name = request_data.get('name', f'erigon_{erigon.id}')

    #   Save the data
    app.user_erigons[user_id][erigon.id] = erigon

    return erigon.api_repr(), 201


@app.route('/stopInstance/<erigon_id>', methods=['POST'])
async def stop_instance(erigon_id):
    user_id = get_user_id()

    try:
        erigon = app.user_erigons[user_id][erigon_id]
    except KeyError:
        return 'Invalid erigon_id', 404

    erigon.stop()

    return erigon.api_repr(), 200
