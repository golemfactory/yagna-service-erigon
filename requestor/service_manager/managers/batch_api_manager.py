from yapapi import Executor, Task, WorkContext
import asyncio
from datetime import timedelta


async def worker(ctx: WorkContext, tasks):
    task = await tasks.__anext__()
    erigon, service_cls = task.data

    if erigon.stopped:
        task.accept_result(result='This erigon was stopped before deployment')
        return

    #   DEPLOYMENT
    service = service_cls(None, ctx)
    try:
        yield await service.start().__anext__()
    except Exception as e:
        print("DEPLOYMENT FAILED ", e)
        task.reject_result(retry=True)
        return

    erigon.set_service(service)

    #   REQUEST PROCESSING
    run = service.run()
    try:
        commit = await run.__anext__()
        while True:
            results_future = yield commit
            commit = await run.asend(results_future)
    except StopAsyncIteration:
        erigon.disable()
        task.accept_result(result='DONE')


class BatchApiManager():
    def __init__(self, service_cls, executor_cfg):
        self.service_cls = service_cls
        self.executor_cfg = executor_cfg

        self.command_queue = asyncio.Queue()
        self.executor_task = asyncio.create_task(self.run())

    def add_instance(self, instance):
        self.command_queue.put_nowait(instance)

    async def stop(self):
        #   Remove all sheduled erigons from queue and stop Executor task generator
        while not self.command_queue.empty():
            self.command_queue.get_nowait()
        self.command_queue.put_nowait('CLOSE')
        await self.executor_task

    async def run(self):
        payload = await self.service_cls.get_payload()

        async with Executor(
            max_workers=100,
            timeout=timedelta(minutes=30),
            payload=payload,
            **self.executor_cfg,
        ) as executor:
            print(
                f"Using subnet: {self.executor_cfg['subnet_tag']}  "
                f"payment driver: {executor.driver}  "
                f"network: {executor.network}\n"
            )
            print(" *** YOU ARE USING BATCH API *** ")

            async def tasks():
                while True:
                    data = await self.command_queue.get()
                    if type(data) is str:
                        assert data == 'CLOSE'
                        break
                    else:
                        task = Task(data=(data, self.service_cls))
                        yield task

            async for task in executor.submit(worker, tasks()):
                print(f"END OF WORK FOR ERIGON {task.data}")
