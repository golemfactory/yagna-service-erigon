import asyncio
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict
import json

from .erigon_payload import ErigonPayload


SECONDS_BETWEEN_UPDATES = 1


@dataclass
class RuntimeState():
    status: str
    url: Optional[str] = None
    auth: Optional[Dict[str, str]] = None
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.now()


class Erigon():
    def __init__(self):
        self.id = self._create_id()
        self.queue = asyncio.Queue()
        self.stopped = False
        self.started = False
        self.runtime_state = RuntimeState('initializing')
        self.update_task = asyncio.create_task(self.update_state())

    @classmethod
    async def get_payload(cls):
        return ErigonPayload()

    async def update_state(self):
        while True:
            if self.stopped:
                self.runtime_state = RuntimeState('stopping')
                break
            res = await self.status()
            self.runtime_state = RuntimeState(**res)
            if not self.stopped:
                #   Additional check for self.stopped because this could have changed
                #   while we awaited for self.status()
                await asyncio.sleep(SECONDS_BETWEEN_UPDATES)

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
        fut = asyncio.get_running_loop().create_future()
        await self.queue.put((cmd, fut))
        await fut
        return fut.result()

    #   FUNCTIONS CALLED FROM INSIDE WORKER
    def start(self, ctx):
        #   NOTE: this ctx.run() is not necessary, but without any ctx.run() it seems that
        #   ctx.commit() does nothing and we would deploy only when first status
        #   request comes
        ctx.run('STATUS')

    async def process_commands(self, ctx):
        queue = self.queue
        while True:
            command, requesting_future = await queue.get()
            if command == 'STATUS':
                ctx.run(command)
                try:
                    processing_future = yield ctx.commit()
                    result = self._parse_status_result(processing_future.result())
                    requesting_future.set_result(result)
                except Exception as e:
                    requesting_future.set_result({'status': f'FAILED: {e}'})
                    self.disable()
                    break
            elif command == 'STOP':
                requesting_future.set_result({'status': 'STOPPING'})
                break

    def _parse_status_result(self, raw_data):
        command_executed = raw_data[0]
        stdout = command_executed.stdout
        mock_echo_data, erigon_data = stdout.split('ERIGON: ', 2)
        erigon_data = json.loads(erigon_data)
        return erigon_data

    def _create_id(self):
        return uuid4().hex

    def __repr__(self):
        return f"{type(self).__name__}[id={self.id}]"
