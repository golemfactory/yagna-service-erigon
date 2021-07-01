import asyncio

from yapapi_service_manager import ServiceManager
from server.erigon_service import Erigon

EXECUTOR_CFG = {
    'budget': 1,
    'subnet_tag': 'erigon',
}


async def run_service(service_manager):
    service_cnt = 1
    start_args = ({'network': 'rinkeby'},)

    services = [service_manager.create_service(Erigon, start_args) for _ in range(service_cnt)]

    for service in services:
        print(f"New service starting: {service}")

    while True:
        for service in services:
            print(f"{service} is {service.status}")
        await asyncio.sleep(1)


def main():
    service_manager = ServiceManager(EXECUTOR_CFG)
    try:
        loop = asyncio.get_event_loop()
        task = loop.create_task(run_service(service_manager))
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        shutdown = loop.create_task(service_manager.close())
        loop.run_until_complete(shutdown)
        task.cancel()


if __name__ == '__main__':
    main()
