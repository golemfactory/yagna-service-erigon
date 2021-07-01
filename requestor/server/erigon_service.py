import asyncio
import json
from typing import TYPE_CHECKING

from yapapi.services import Service

from .erigon_payload import ErigonPayload

if TYPE_CHECKING:
    from typing import List
    from yapapi.events import CommandExecuted


class Erigon(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = None
        self.auth = None

        #   NOTE: this is the network provider says it is running on, not the one
        #         requested (although these two should match)
        self.network = None

    @classmethod
    async def get_payload(cls):
        return ErigonPayload()

    async def start(self):
        #   startup - set start args (network parameter)
        self._ctx.deploy()
        start_args = await self._get_start_args()
        if start_args:
            erigon_init_args = start_args[0]
            erigon_init_args_str = json.dumps(erigon_init_args)
            self._ctx.start(erigon_init_args_str)
        else:
            self._ctx.start()

        #   Set url & auth
        self._ctx.run('STATUS')
        processing_future = yield self._ctx.commit()
        result = self._parse_status_result(processing_future.result())
        self.url, self.auth, self.network = result['url'], result['auth'], result['network']

    @staticmethod
    def _parse_status_result(raw_data: 'List[CommandExecuted]'):
        #   NOTE: raw_data contains also output from "start" and "deploy" for the first
        #         request, and only single row for subsequent requests -> that's why -1 not 0
        command_executed = raw_data[-1]

        erigon_data = command_executed.stdout or ''  # FIXME: Handle missing/invalid output
        erigon_data = json.loads(erigon_data)
        return erigon_data

    async def _get_start_args(self):
        #   TODO: this is part of the ugly start-passing-protocol & will change
        #         when yapapi issue 372 is fixed
        while True:
            try:
                return self._cluster.instance_start_args
            except AttributeError:
                await asyncio.sleep(0.1)
