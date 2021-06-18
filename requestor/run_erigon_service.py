import asyncio

from service_manager import ServiceManager
from server.erigon_service import Erigon

EXECUTOR_CFG = {
    'budget': 1,
    'subnet_tag': 'erigon',
}


async def main(service_manager):
    service_cnt = 1
    start_args = [{'network': 'rinkeby'}]

    services = [service_manager.create_service(Erigon, start_args) for _ in range(service_cnt)]

    for service in services:
        print(f"New service starting: {service}")

    while True:
        for service in services:
            print(f"{service} is {service.status}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    service_manager = ServiceManager(EXECUTOR_CFG)
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(main(service_manager))
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        shutdown = loop.create_task(service_manager.close())
        loop.run_until_complete(shutdown)
        main_task.cancel()
