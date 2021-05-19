import asyncio
from yapapi import WorkContext


async def worker(ctx: WorkContext, tasks):
    async for task in tasks:
        break
    queue = task.data['queue']
    deployment_fut = queue.get_nowait()

    print("DEPLOYING")
    ctx.run('STATUS')
    yield ctx.commit()
    deployment_fut.set_result({'status': 'DEPLOYED'})
    queue.task_done()

    print("WORKING")
    await asyncio.sleep(1)
    while True:
        command, req_fut = await queue.get()
        if command == 'STATUS':
            ctx.run(command)
            out = yield ctx.commit()
            req_fut.set_result(out.result())
            queue.task_done()
        elif command == 'STOP':
            req_fut.set_result({'status': 'STOPPING'})
            break
    task.accept_result(result='DONE')
