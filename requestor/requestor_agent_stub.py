import asyncio

from service_manager import ServiceManager
import erigon_services

from server import erigon_data


async def main(sm):
    service_cnt = 1
    services = [sm.create_service(erigon_services.Erigon) for _ in range(service_cnt)]
    for service in services:
        print(f"New service starting: {service}")

    while True:
        for service in services:
            print(f"{service} status: {erigon_data(service)}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    sm = ServiceManager()
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(main(sm))
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        shutdown = loop.create_task(sm.close())
        loop.run_until_complete(shutdown)
        main_task.cancel()
