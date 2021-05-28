from yapapi import Executor, Task, WorkContext
import asyncio


async def worker(ctx: WorkContext, tasks):
    task = await tasks.__anext__()
    erigon = task.data
    erigon._ctx = ctx

    if erigon.stopped:
        task.accept_result(result='This erigon was stopped before deployment')
        return

    #   DEPLOYMENT
    try:
        erigon.start(ctx)
        yield ctx.commit()
    except Exception as e:
        print("DEPLOYMENT FAILED ", e)
        task.reject_result(retry=True)
        return
    erigon.started = True

    #   REQUEST PROCESSING
    run = erigon.process_commands(ctx)
    try:
        commit = await run.__anext__()
        while True:
            results_future = yield commit
            commit = await run.asend(results_future)
    except StopAsyncIteration:
        task.accept_result(result='DONE')

class PseudoContext():
    def __init__(self):
        self.id = 'PseudoIDThatWillBeReplaced'

class BatchApiManager():
    def __init__(self, service_cls, executor_cfg):
        print(" *** YOU ARE USING BATCH API *** ")
        self.service_cls = service_cls
        self.executor_cfg = executor_cfg

        self.command_queue = asyncio.Queue()
        self.executor_task = asyncio.create_task(self.run())

    def add_instance(self):
        instance = self.service_cls(None, PseudoContext())
        self.command_queue.put_nowait(instance)
        return instance

    async def stop(self):
        #   Remove all sheduled erigons from queue and stop Executor task generator
        while not self.command_queue.empty():
            self.command_queue.get_nowait()
        self.command_queue.put_nowait('CLOSE')
        await self.executor_task

    async def run(self):
        payload = await self.service_cls.get_payload()

        async with Executor(
            payload=payload,
            **self.executor_cfg,
        ) as executor:
            print(
                f"Using subnet: {self.executor_cfg['subnet_tag']}  "
                f"payment driver: {executor.driver}  "
                f"network: {executor.network}\n"
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
