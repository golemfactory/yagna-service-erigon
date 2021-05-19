import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from uuid import uuid4
from turbogeth_payload import TurbogethPayload
from yapapi import Executor, Task
from datetime import timedelta
from worker import worker

STATUS_MSG = {
    'status': 'running',
    'url': 'www.example.com:868767',
    'secret': 'THIS IS SECRET!',
}
SUBNET_TAG = 'ttt'


class Erigon():
    def __init__(self):
        self.id = self._create_id()
        self.queue = asyncio.Queue()

    async def start(self):
        fut = asyncio.get_running_loop().create_future()
        await self.queue.put(fut)
        await fut

        if fut.result() != {'status': 'DEPLOYED'}:
            raise Exception(f'Failed to start Erigon: {fut.result()}')

        #   TODO: fut.result() is the only place we might access the message
        #         returned by Runtime.deploy() - but do we want it?

    async def status(self):
        return self.run('STATUS')

    async def stop(self):
        return self.run('STOP')

    async def run(self, cmd):
        fut = asyncio.get_running_loop().create_future()
        self.queue.put_nowait((cmd, fut))
        await fut
        return fut.result()

    def _create_id(self):
        return uuid4().hex


class YagnaErigonManager():
    def __init__(self):
        enable_default_logger(log_file='log.log')
        self.executor_task = None
        self.tasks_queue = asyncio.Queue()
        self.closing = False

    async def deploy_erigon(self):

        if self.executor_task is None:
            self.executor_task = asyncio.create_task(self._create_executor())

        erigon = Erigon()
        self.tasks_queue.put_nowait(erigon)

        print("START")
        await erigon.start()
        print("STARTED")

        return erigon

    async def close(self):
        self.closing = True
        await self.executor_task

    async def _create_executor(self):
        async with Executor(
            payload=TurbogethPayload(),
            max_workers=1,
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
                    if self.closing:
                        break
                    erigon = await self.tasks_queue.get()
                    task = Task(data=erigon)
                    yield task

            async for _ in executor.submit(worker, tasks()):
                pass
