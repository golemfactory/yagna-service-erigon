import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict
import json

from .erigon_payload import ErigonPayload

from yapapi.executor.services import Service

SECONDS_BETWEEN_UPDATES = 1


@dataclass
class RuntimeState():
    status: str
    url: Optional[str] = None
    auth: Optional[Dict[str, str]] = None
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.now()


class ErigonService(Service):
    @classmethod
    async def get_payload(cls):
        return ErigonPayload()

    async def start(self):
        #   NOTE: this ctx.run() is not necessary, but without any ctx.run() it seems that
        #   ctx.commit() does nothing and we would deploy only when first status
        #   request comes
        #   TODO this is required only by old API I think? --> move to BatchApiManager
        self._ctx.run('STATUS')
        yield self._ctx.commit()

    async def run(self):
        while True:
            service_signal = await self._listen()
            command = service_signal.message
            if command == 'STATUS':
                self._ctx.run(command)
                try:
                    processing_future = yield self._ctx.commit()
                    result = self._parse_status_result(processing_future.result())
                    self._respond_nowait(result, service_signal)
                except Exception as e:
                    result = {'status': f'FAILED: {e}'}
                    self._respond_nowait(result, service_signal)
                    break
            elif command == 'STOP':
                result = {'status': 'STOPPING'}
                self._respond_nowait(result, service_signal)
                break

    def _parse_status_result(self, raw_data):
        command_executed = raw_data[0]
        stdout = command_executed.stdout
        mock_echo_data, erigon_data = stdout.split('ERIGON: ', 2)
        erigon_data = json.loads(erigon_data)
        return erigon_data


class Erigon():
    service_cls = ErigonService

    def __init__(self):
        self.stopped = False
        self.runtime_state = RuntimeState('initializing')
        self.update_task = asyncio.create_task(self.update_state())
        self.service = None

    def set_service(self, service):
        self.service = service

    @property
    def started(self):
        return self.service is not None

    @property
    def id(self):
        if self.service:
            return self.service.id
        return '[NOT STARTED YET]'

    async def status(self):
        return await self.run_single_command('STATUS')

    async def stop(self):
        if self.stopped:
            return

        self.disable()
        if self.started:
            return await self.run_single_command('STOP')
        else:
            return "not started yet"

    def disable(self):
        if self.stopped:
            return
        self.stopped = True
        print(f"STOPPING {self}")

    async def run_single_command(self, cmd):
        self.service.send_message_nowait(cmd)
        service_signal = await self.service.receive_message()
        #   TODO: how do we check if we got response for the signal sent?
        #         this is irrelevant now, but could be useful in the future
        return service_signal.message

    async def update_state(self):
        while True:
            if self.stopped:
                self.runtime_state = RuntimeState('stopping')
                break
            if not self.started:
                self.runtime_state = RuntimeState('starting')
                await asyncio.sleep(1)
                continue

            res = await self.status()
            self.runtime_state = RuntimeState(**res)
            if not self.stopped:
                #   Additional check for self.stopped because this could have changed
                #   while we awaited for self.status()
                await asyncio.sleep(SECONDS_BETWEEN_UPDATES)

    def __repr__(self):
        return f"{type(self).__name__}[id={self.id}]"
