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


class YagnaErigonManager():
    def __init__(self):
        enable_default_logger(log_file='log.log')
        self.executor_task = None
        self.id = self._create_id()
        self.queue = asyncio.Queue()

    async def close(self):
        if self.executor_task is not None:
            await self.executor_task
            self.executor_task = None

    async def deploy(self):
        if self.executor_task is None:
            self.executor_task = asyncio.create_task(self._create_executor())

        fut = asyncio.get_running_loop().create_future()
        self.queue.put_nowait(fut)

        await fut

        if fut.result() != {'status': 'DEPLOYED'}:
            raise Exception(f'Failed to start provider: {fut.result()}')

        return {
            'deploy_msg': {'valid': 1},
            'start_msg': None,
            'status_msg': STATUS_MSG,
        }

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

            task = Task(data={'queue': self.queue})
            async for _ in executor.submit(worker, [task]):
                pass

    async def status(self):
        fut = asyncio.get_running_loop().create_future()
        self.queue.put_nowait(('STATUS', fut))
        await fut
        return fut.result()

    async def stop(self):
        fut = asyncio.get_running_loop().create_future()
        self.queue.put_nowait(('STOP', fut))
        await fut
        return fut.result()

    def _create_id(self):
        return uuid4().hex
