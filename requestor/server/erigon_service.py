import json
from datetime import datetime
from typing import TYPE_CHECKING

from yapapi.services import Service, ServiceState

from .erigon_payload import ErigonPayload

if TYPE_CHECKING:
    from typing import List, Optional
    from yapapi.events import CommandExecuted


class Erigon(Service):
    def __init__(self, name: 'Optional[str]', init_params: 'Optional[dict]', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url: 'Optional[str]' = None
        self.auth: Optional['dict'] = None
        self.name = name or f'erigon_{self.id}'
        self.init_params = init_params
        self.created_at = datetime.utcnow()
        self.stopped_at: 'Optional[datetime]' = None
        #   NOTE: this is the network provider says it is running on, not the one
        #         requested (although these two should match)
        self.eth_network: 'Optional[str]' = None

    @classmethod
    async def get_payload(cls):
        return ErigonPayload()

    async def start(self):
        #   startup - set start args (network parameter)
        await self._ctx.deploy()
        if self.init_params:
            await self._ctx.start(json.dumps(self.init_params))
        else:
            await self._ctx.start()

        #   Set url & auth
        await self._ctx.run('STATUS')
        processing_future = yield self._ctx.commit()
        result = self._parse_status_result(processing_future.result())
        self.url, self.auth, self.eth_network = result['url'], result['auth'], result.get('network', 'mainnet')

    async def stop(self):
        self.cluster.stop()
        if self.stopped_at is None:
            self.stopped_at = datetime.utcnow()

    @staticmethod
    def _parse_status_result(raw_data: 'List[CommandExecuted]'):
        #   NOTE: raw_data contains also output from "start" and "deploy" for the first
        #         request, and only single row for subsequent requests -> that's why -1 not 0
        command_executed = raw_data[-1]

        erigon_data = command_executed.stdout or ''  # FIXME: Handle missing/invalid output
        erigon_data = json.loads(erigon_data)
        return erigon_data

    def api_repr(self):
        data = {
            'id': str(self.id),
            'status': self.state.name,
            'name': self.name,
            'init_params': self.init_params,
            'created_at': self.created_at.isoformat(),
        }
        if self.state is ServiceState.running:
            data['url'] = self.url
            data['auth'] = self.auth
            data['network'] = self.eth_network
        elif self.state is ServiceState.terminated:
            data['stopped_at'] = self.stopped_at.isoformat()

        return data
