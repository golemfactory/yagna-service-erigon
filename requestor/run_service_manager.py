import asyncio

from service_manager import ServiceManager
import erigon_services


def state(service_wrapper):
    if service_wrapper.stopped:
        status = 'stopped'
    elif not service_wrapper.started:
        status = 'pending'
    else:
        #   NOTE: this is erigon-specific thing, we don't use state of instance
        #   beacues from our POV it is "running" when we know the url
        if service_wrapper.service.url is None:
            status = 'starting'
        else:
            status = 'running'

    if status == 'running':
        return f'running on {service_wrapper.service.network}'
    return status


async def main(service_manager):
    service_cnt = 1
    service_cls = erigon_services.Erigon
    start_args = [{'network': 'kovan'}]

    services = [service_manager.create_service(service_cls, start_args) for _ in range(service_cnt)]

    for service in services:
        print(f"New service starting: {service}")

    while True:
        for service in services:
            print(f"{service} state: {state(service)}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    service_manager = ServiceManager({'subnet_tag': 'erigon'})
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(main(service_manager))
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        shutdown = loop.create_task(service_manager.close())
        loop.run_until_complete(shutdown)
        main_task.cancel()
