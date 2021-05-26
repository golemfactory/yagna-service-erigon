import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from yapapi import Executor, Task
from worker import worker
from datetime import timedelta

DEFAULT_EXECUTOR_CFG = {
    'max_workers': 100,
    'budget': 1.0,
    'timeout': timedelta(minutes=30),
    'subnet_tag': 'ttt',
    'event_consumer': log_summary(log_event_repr),
}


class YagnaErigonManager():
    def __init__(self, executor_cfg={}):
        self.executor_cfg = DEFAULT_EXECUTOR_CFG.copy()
        self.executor_cfg.update(executor_cfg)

        enable_default_logger(log_file='log.log')
        self.command_queue = asyncio.Queue()
        self.erigons = []
        self.executor_task = None

    def create_erigon(self, cls):
        if self.executor_task is None:
            self.executor_task = asyncio.create_task(self._create_executor(cls.payload))

        erigon = cls()
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

    async def _create_executor(self, payload):
        async with Executor(
            payload=payload,
            **self.executor_cfg,
        ) as executor:
            print(
                f"Using subnet: {self.executor_cfg['subnet_tag']}."
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
