from yagna_erigon_manager import YagnaErigonManager
import asyncio


async def main():
    yem = YagnaErigonManager()
    erigon = await yem.deploy_erigon()
    print(f"New Erigon deployed, id: {erigon.id}")

    await yem.close()
    # erigon = await yem.deploy_erigon()


    # # for i in range(2):
    # #     status = await erigon.status()
    # #     print(f"Erigon {erigon.id} status: {status}")

    # # stop_result = await erigon.stop()
    # # print(f"Erigon {yem.id} stopped: {stop_result}")
    # 
    # print("AWAITED")
    

if __name__ == '__main__':
    asyncio.run(main())
    print("END")
