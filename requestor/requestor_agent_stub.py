import asyncio

from service_manager import YagnaErigonManager, services


async def main(yem):
    erigon = yem.create_erigon(services.Erigon)
    print(f"New Erigon starting, id: {erigon.id}")

    while True:
        print(f"Erigon {erigon.id} update: {erigon.runtime_state.timestamp} "
              f"status: {erigon.runtime_state.status} url: {erigon.runtime_state.url}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    yem = YagnaErigonManager()
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(main(yem))
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        shutdown = loop.create_task(yem.close())
        loop.run_until_complete(shutdown)
        main_task.cancel()
