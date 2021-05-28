from yapapi.payload import vm
from yapapi.executor.services import Service

STARTING_RESULT = {'status': 'starting', 'url': None, 'auth': None}
RUNNING_RESULT = {
    'status': 'running',
    'url': 'www.some.where/erigon:7987',
    'auth': {
        'user': 'SECRET_USER',
        'password': 'SECRET_PASSWORD',
    }
}


class PseudoErigonService(Service):
    def post_init(self):
        self._status_call_cnt = 0

    @classmethod
    async def get_payload(cls):
        #   NOTE: this is a blender image
        #         (because every provider has it downloaded)
        return await vm.repo(
            image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
            min_mem_gib=0.5,
            min_storage_gib=2.0,
        )

    async def start(self):
        self._ctx.run("/bin/echo", "STATUS")
        yield self._ctx.commit()

    async def run(self):
        while True:
            service_signal = await self._listen()
            command = service_signal.message
            if command == 'STATUS':
                self._ctx.run("/bin/echo", "STATUS")
                try:
                    yield self._ctx.commit()
                    if self._status_call_cnt < 2:
                        self._respond_nowait(STARTING_RESULT, service_signal)
                        self._status_call_cnt += 1
                    else:
                        self._respond_nowait(RUNNING_RESULT, service_signal)
                except Exception as e:
                    result = {'status': f'FAILED: {e}'}
                    self._respond_nowait(result, service_signal)
                    break
            elif command == 'STOP':
                result = {'status': 'STOPPING'}
                self._respond_nowait(result, service_signal)
                break
