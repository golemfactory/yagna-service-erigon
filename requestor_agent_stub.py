from yagna_erigon_manager import YagnaErigonManager
import asyncio


async def main():
    yem = YagnaErigonManager()
    erigon = await yem.deploy_erigon()
    print(f"New Erigon deployed, id: {erigon.id}")

    for i in range(3):
        status = await erigon.status()
        print(f"Erigon {erigon.id} status: {status}")

    stop_result = await erigon.stop()
    print(f"Erigon {erigon.id} stopped: {stop_result}")

    await yem.close()


if __name__ == '__main__':
    asyncio.run(main())
