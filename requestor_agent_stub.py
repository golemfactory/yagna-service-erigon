from yagna_erigon_manager import YagnaErigonManager
import asyncio

async def main():
    yam = YagnaErigonManager()
    deploy_result = await yam.deploy()
    print(f"New Erigon deployed, id: {yam.id}")
    print(f"Deployment status: {deploy_result}")
    for i in range(5):
        await asyncio.sleep(0.5)
        status = await yam.status()
        print(f"Erigon {yam.id} status: {status}")

    stop_result = await yam.stop()
    print(f"Erigon {yam.id} stopped: {stop_result}")

if __name__ == '__main__':
    asyncio.run(main())
