from collections import defaultdict
import json
from typing import TYPE_CHECKING
from eth_account.datastructures import HexBytes

from quart import Quart, request, abort, jsonify
from quart_cors import cors
from yapapi import Golem
from web3 import Web3


from .erigon_service import Erigon
from ..utils import generate_message, validate_massage

MESSAGE_VALIDATION = False

if TYPE_CHECKING:
    from typing import Optional, MutableMapping, Dict, Any


class App(Quart):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.user_erigons: 'MutableMapping[str, MutableMapping[str, Erigon]]' = defaultdict(dict)
        self.golem: 'Optional[Golem]' = None

        # It should be reconfigured before starting the app
        self.yapapi_executor_config: 'Dict[str, Any]' = {'budget': 0}


app = App()
cors(app)


@app.before_serving
async def start_golem():
    app.golem = Golem(**app.yapapi_executor_config)
    await app.golem.start()


@app.after_serving
async def stop_golem():
    await app.golem.stop()


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


def validate_message(user_id: str) -> None:
    try:
        signature = HexBytes(request.headers['Signature'])
    except KeyError:
        abort_json_400('Missing signature header')
    try:
        message = request.headers['Message']
    except KeyError:
        abort_json_400('Missing message header')
    if not validate_massage(user_id, signature, message):
        abort_json_400('Invalid signature')


@app.route('/getInstances', methods=['GET'])
async def get_instances():
    user_id = get_user_id()
    if MESSAGE_VALIDATION:
        validate_message(user_id)
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
    try:
        cluster = await app.golem.run_service(Erigon, instance_params=[{
            "name": request_data.get('name'),
            "init_params": init_params
        }])
        erigon = cluster.instances[0]
    except Exception:  # pylint: disable=broad-except
        # TODO: Log error message
        return "service initialization failed", 500

    #   Save the data
    app.user_erigons[user_id][str(erigon.id)] = erigon

    return erigon.api_repr(), 201


@app.route('/stopInstance/<erigon_id>', methods=['POST'])
async def stop_instance(erigon_id):
    user_id = get_user_id()

    try:
        erigon = app.user_erigons[user_id][erigon_id]
    except KeyError:
        return 'invalid instance ID', 404

    await erigon.stop()

    return erigon.api_repr(), 200


@app.route('/getMessage', methods=['GET'])
async def get_message():
    return json.dumps(generate_message(20)), 200
