from yapapi.executor import Golem
import asyncio


class YapapiConnector():
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
        async with Golem(**self.executor_cfg) as golem:
            print(
                f"Using subnet: {self.executor_cfg['subnet_tag']}  "
                f"payment driver: {golem.driver}  "
                f"network: {golem.network}\n"
            )
            while True:
                data = await self.command_queue.get()
                if type(data) is str:
                    assert data == 'CLOSE'
                    break
                else:
                    erigon = data
                    cluster = await golem.run_service(self.service_cls)
                    while not cluster.instances:
                        await asyncio.sleep(1)
                    erigon.set_service(cluster.instances[0])
