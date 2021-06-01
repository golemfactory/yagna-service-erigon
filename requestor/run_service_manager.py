import asyncio

from service_manager import ServiceManager
import erigon_services


def state(service_wrapper):
    if not service_wrapper.started:
        status = 'pending'
    elif service_wrapper.stopped:
        status = 'stopped'
    else:
        #   NOTE: this is erigon-specific thing, we don't use state of instance
        #   beacues from our POV it is "running" when we know the url
        if service_wrapper.service.url is None:
            status = 'starting'
        else:
            status = 'running'
    return status


async def main(sm):
    service_cnt = 2
    service_cls = erigon_services.PseudoErigon   # this runs on devnet and pretends to be an Erigon
    services = [sm.create_service(service_cls) for _ in range(service_cnt)]

    for service in services:
        print(f"New service starting: {service}")

    while True:
        for service in services:
            print(f"{service} state: {state(service)}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    sm = ServiceManager({'subnet_tag': 'devnet-beta.1'})
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(main(sm))
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        shutdown = loop.create_task(sm.close())
        loop.run_until_complete(shutdown)
        main_task.cancel()
