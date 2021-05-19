STATUS_MSG = {
    'status': 'running',
    'url': 'www.example.com:868767',
    'secret': 'THIS IS SECRET!',
}


class YagnaErigonManager():
    def __init__(self):
        self.id = self._create_id()

    async def deploy(self):
        return {
            'deploy_msg': {'valid': 1},
            'start_msg': None,
            'status_msg': STATUS_MSG,
        }

    async def status(self):
        return STATUS_MSG

    async def stop(self):
        return {'stop': 'ping'}

    def _create_id(self):
        return 1
