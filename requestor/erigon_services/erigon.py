import json
import asyncio

from .erigon_payload import ErigonPayload

from yapapi.executor.services import Service

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from yapapi.executor.events import CommandExecuted


class Erigon(Service):
    def post_init(self):
        self.url = None
        self.auth = None

    @classmethod
    async def get_payload(cls):
        return ErigonPayload()

    async def run(self):
        #   Set url & auth
        self._ctx.run('STATUS')
        processing_future = yield self._ctx.commit()
        result = self._parse_status_result(processing_future.result())
        self.url, self.auth = result['url'], result['auth']

        #   Wait forever
        await asyncio.sleep(9999999999999999)

        #   This function must be a generator, so we need a yield
        yield

    def _parse_status_result(self, raw_data: 'List[CommandExecuted]'):
        #   NOTE: raw_data contains also output from "start" and "deploy" for the first
        #         request, and only single row for subsequent requests -> that's why -1 not 0
        command_executed = raw_data[-1]

        stdout = command_executed.stdout
        mock_echo_data, erigon_data = stdout.split('ERIGON: ', 2)
        erigon_data = json.loads(erigon_data)
        return erigon_data
