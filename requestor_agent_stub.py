from yagna_erigon_manager import YagnaErigonManager
import asyncio


async def main():
    yam = YagnaErigonManager()
    deploy_task, deploy_result = await yam.deploy()
    print(f"New Erigon deployed, id: {yam.id}, Deployment status: {deploy_result}")

    for i in range(5):
        status = await yam.status()
        print(f"Erigon {yam.id} status: {status}")

    stop_result = await yam.stop()
    print(f"Erigon {yam.id} stopped: {stop_result}")
    
    await deploy_task

if __name__ == '__main__':
    asyncio.run(main())
    print("END")
