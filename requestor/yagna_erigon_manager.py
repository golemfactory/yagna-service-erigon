import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from uuid import uuid4
from erigon_payload import ErigonPayload
from yapapi import Executor, Task
from datetime import timedelta, datetime
from worker import worker

from dataclasses import dataclass, field
from typing import Optional

SUBNET_TAG = 'ttt'
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
        self.disable()
        print(f"STOPPING {self}")
        if self.started:
            return await self.run('STOP')
        else:
            return "not started yet"

    def disable(self):
        if self.stopped:
            return
        self.stopped = True

    async def run(self, cmd):
        fut = asyncio.get_running_loop().create_future()
        await self.queue.put((cmd, fut))
        await fut
        return fut.result()

    def _create_id(self):
        return uuid4().hex

    def __repr__(self):
        return f"{type(self).__name__}[id={self.id}]"


class YagnaErigonManager():
    def __init__(self):
        enable_default_logger(log_file='log.log')
        self.command_queue = asyncio.Queue()
        self.erigons = []
        self.executor_task = None

    def create_erigon(self):
        if self.executor_task is None:
            self.executor_task = asyncio.create_task(self._create_executor())
        erigon = Erigon()
        self.command_queue.put_nowait(erigon)
        self.erigons.append(erigon)
        return erigon

    async def close(self):
        #   Remove all sheduled erigons from queue and stop Executor task generator
        while not self.command_queue.empty():
            self.command_queue.get_nowait()
        self.command_queue.put_nowait('CLOSE')

        #   Stop all Erigons & wait for the Executor to finish
        tasks = [erigon.stop() for erigon in self.erigons]
        if self.executor_task is not None:
            tasks.append(self.executor_task)

        await asyncio.gather(*tasks)

    async def _create_executor(self):
        async with Executor(
            payload=ErigonPayload(),
            max_workers=2,
            budget=1.0,
            timeout=timedelta(minutes=30),
            subnet_tag=SUBNET_TAG,
            event_consumer=log_summary(log_event_repr),
        ) as executor:
            print(
                f"Using subnet: {SUBNET_TAG}."
                f"payment driver: {executor.driver}, "
                f"and network: {executor.network}\n"
            )

            async def tasks():
                while True:
                    data = await self.command_queue.get()
                    if type(data) is str:
                        assert data == 'CLOSE'
                        break
                    else:
                        task = Task(data=data)
                        yield task

            async for task in executor.submit(worker, tasks()):
                print(f"END OF WORK FOR ERIGON {task.data}")
