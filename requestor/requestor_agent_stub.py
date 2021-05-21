from yagna_erigon_manager import YagnaErigonManager
import asyncio


async def main(yem):
    erigon = yem.create_erigon()
    await erigon.start()
    print(f"New Erigon deployed, id: {erigon.id}")

    while True:
        status = await erigon.status()
        print(f"Erigon {erigon.id} status: {status}")

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
