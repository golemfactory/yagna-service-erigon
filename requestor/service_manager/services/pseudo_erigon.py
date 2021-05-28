from .erigon import Erigon
from yapapi.payload import vm

STARTING_RESULT = {'status': 'starting', 'url': None, 'auth': None}
RUNNING_RESULT = {
    'status': 'running',
    'url': 'www.some.where/erigon:7987',
    'auth': {
        'user': 'SECRET_USER',
        'password': 'SECRET_PASSWORD',
    }
}


class PseudoErigon(Erigon):
    def __init__(self):
        super().__init__()
        self._status_call_cnt = 0

    @classmethod
    async def get_payload(cls):
        return await vm.repo(
            image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
            min_mem_gib=0.5,
            min_storage_gib=2.0,
        )

    def start(self, ctx):
        ctx.run('/bin/echo', "START")

    async def process_commands(self, ctx):
        queue = self.queue
        while True:
            command, requesting_future = await queue.get()
            if command == 'STATUS':
                ctx.run('/bin/echo', 'STATUS')
                try:
                    yield ctx.commit()
                    if self._status_call_cnt < 2:
                        result = STARTING_RESULT
                        self._status_call_cnt += 1
                    else:
                        result = RUNNING_RESULT
                    requesting_future.set_result(result)
                except Exception as e:
                    requesting_future.set_result({'status': f'FAILED: {e}'})
                    self.disable()
                    break
            elif command == 'STOP':
                requesting_future.set_result({'status': 'STOPPING'})
                break
