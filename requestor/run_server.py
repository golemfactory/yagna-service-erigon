import os

from .server.app import app

app.yapapi_executor_config = {
    #   NOTE: budget == 10 is not enough to make it run for long
    'budget': 10,
    'subnet_tag': os.environ.get('SUBNET_TAG', 'erigon'),
}

if __name__ == '__main__':
    app.run(host='0.0.0.0')
