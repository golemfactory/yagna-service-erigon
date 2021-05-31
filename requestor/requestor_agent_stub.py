import asyncio

from service_manager import YagnaErigonManager, services

from server import erigon_data


async def main(yem):
    erigons = [yem.create_erigon(services.Erigon) for e in range(1)]
    for erigon in erigons:
        print(f"New Erigon starting, id: {erigon.id}")

    while True:
        for erigon in erigons:
            print(f"Erigon {erigon.id} status: {erigon_data(erigon)}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    # yem = YagnaErigonManager()
    yem = YagnaErigonManager({'subnet_tag': 'ttt2'})
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(main(yem))
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        shutdown = loop.create_task(yem.close())
        loop.run_until_complete(shutdown)
        main_task.cancel()
