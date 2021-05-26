from .erigon import Erigon
from yapapi.payload import vm

STARTING_RESULT = {'status': 'starting', 'url': None, 'secret': None}
RUNNING_RESULT = {'status': 'running', 'url': 'www.some.where/erigon:7987', 'secret': 'AAAUTH'}


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
                def on_success(processing_future):
                    if self._status_call_cnt < 5:
                        result = STARTING_RESULT
                        self._status_call_cnt += 1
                    else:
                        result = RUNNING_RESULT
                    requesting_future.set_result(result)

                def on_failure():
                    requesting_future.set_result({'status': 'FAILED'})

                ctx.run('/bin/echo', 'STATUS')
                yield on_success, on_failure
            elif command == 'STOP':
                requesting_future.set_result({'status': 'STOPPING'})
                break
