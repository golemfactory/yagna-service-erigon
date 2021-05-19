from yapapi import WorkContext


async def worker(ctx: WorkContext, tasks):
    task = await tasks.__anext__()
    erigon = task.data
    queue = erigon.queue

    deployment_fut = await queue.get()

    print("DEPLOYING")

    ctx.run('STATUS')
    yield ctx.commit()
    deployment_fut.set_result({'status': 'DEPLOYED'})
    
    print("AFTER DEPLOYED")

    while True:
        command, req_fut = await queue.get()
        if command == 'STATUS':
            ctx.run(command)
            out = yield ctx.commit()
            req_fut.set_result(out.result())
            queue.task_done()
        elif command == 'STOP':
            req_fut.set_result({'status': 'STOPPING'})
            print("STOPPING")
            queue.task_done()
            break
    
    print("DONE")
    task.accept_result(result='DONE')
