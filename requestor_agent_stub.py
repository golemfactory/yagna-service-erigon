from yagna_erigon_manager import YagnaErigonManager
import asyncio


async def print_status(erigon):
    status = await erigon.status()
    print(f"Erigon {erigon.id} status: {status}")


async def main():
    yem = YagnaErigonManager()

    erigons = []
    for _ in range(0, 3):
        erigons.append(await yem.deploy_erigon())

    tasks = []
    for i in range(3):
        tasks += [print_status(erigon) for erigon in erigons]

    await asyncio.gather(*tasks)

    for erigon in erigons:
        stop_result = await erigon.stop()
        print(f"Erigon {erigon.id} stopped: {stop_result}")

    await yem.close()


if __name__ == '__main__':
    asyncio.run(main())
