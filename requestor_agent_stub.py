from yagna_erigon_manager import YagnaErigonManager
import asyncio


async def print_status(erigon):
    status = await erigon.status()
    print(f"Erigon {erigon.id} status: {status}")


async def main():
    yem = YagnaErigonManager()

    #   Create 3 erigons
    erigons = []
    for _ in range(0, 3):
        erigon = await yem.deploy_erigon()
        await print_status(erigon)
        erigons.append(erigon)

    #   Check the status concurrently
    tasks = []
    for i in range(3):
        tasks += [print_status(erigon) for erigon in erigons]
    await asyncio.gather(*tasks)

    #   Kill one of the erigons
    stop_result = await erigons[0].stop()
    erigons = erigons[1:]
    print(f"Erigon {erigons[0].id} stopped: {stop_result}")

    #   Ensure other erigons are still alive and well
    tasks = []
    for i in range(3):
        tasks += [print_status(erigon) for erigon in erigons]
    await asyncio.gather(*tasks)

    #   Stop other erigons
    for erigon in erigons:
        stop_result = await erigon.stop()
        print(f"Erigon {erigon.id} stopped: {stop_result}")

    await yem.close()


if __name__ == '__main__':
    asyncio.run(main())
