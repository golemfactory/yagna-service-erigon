from typing import Optional, Dict
from dataclasses import dataclass, field
import asyncio
from datetime import datetime

SECONDS_BETWEEN_UPDATES = 1


@dataclass
class RuntimeState():
    status: str
    url: Optional[str] = None
    auth: Optional[Dict[str, str]] = None
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.now()


class ServiceWrapper():
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
