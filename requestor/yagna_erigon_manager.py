import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from yapapi import Executor, Task
from worker import worker
from datetime import timedelta

from services import Erigon

SUBNET_TAG = 'ttt'


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
            payload=Erigon.payload,
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
