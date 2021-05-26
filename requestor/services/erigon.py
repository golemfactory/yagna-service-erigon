import asyncio
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from .erigon_payload import ErigonPayload


SECONDS_BETWEEN_UPDATES = 1


@dataclass
class RuntimeState():
    status: str
    url: Optional[str] = None
    secret: Optional[str] = None
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.now()


class Erigon():
    payload = ErigonPayload()

    def __init__(self):
        self.id = self._create_id()
        self.queue = asyncio.Queue()
        self.stopped = False
        self.started = False
        self.runtime_state = RuntimeState('initializing')
        self.update_task = asyncio.create_task(self.update_state())

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
        return await self.run('STATUS')

    async def stop(self):
        if self.stopped:
            return

        self.disable()
        if self.started:
            return await self.run('STOP')
        else:
            return "not started yet"

    def disable(self):
        if self.stopped:
            return
        self.stopped = True
        print(f"STOPPING {self}")

    async def run(self, cmd):
        fut = asyncio.get_running_loop().create_future()
        await self.queue.put((cmd, fut))
        await fut
        return fut.result()

    def _create_id(self):
        return uuid4().hex

    def __repr__(self):
        return f"{type(self).__name__}[id={self.id}]"
