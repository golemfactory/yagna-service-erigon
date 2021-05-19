from yagna_erigon_manager import YagnaErigonManager
import asyncio


async def main():
    yem = YagnaErigonManager()
    deploy_result = await yem.deploy()
    print(f"New Erigon deployed, id: {yem.id}, Deployment status: {deploy_result}")

    for i in range(2):
        status = await yem.status()
        print(f"Erigon {yem.id} status: {status}")

    stop_result = await yem.stop()
    print(f"Erigon {yem.id} stopped: {stop_result}")

    await yem.close()
    

if __name__ == '__main__':
    asyncio.run(main())
    print("END")
