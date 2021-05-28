from yapapi import WorkContext


async def worker(ctx: WorkContext, tasks):
    task = await tasks.__anext__()
    erigon = task.data

    if erigon.stopped:
        task.accept_result(result='This erigon was stopped before deployment')
        return

    #   DEPLOYMENT
    try:
        erigon.start(ctx)
        yield ctx.commit()
    except Exception as e:
        print("DEPLOYMENT FAILED ", e)
        task.reject_result(retry=True)
        return
    erigon.started = True

    #   REQUEST PROCESSING
    run = erigon.process_commands(ctx)
    try:
        commit = await run.__anext__()
        while True:
            results_future = yield commit
            commit = await run.asend(results_future)
    except StopAsyncIteration:
        task.accept_result(result='DONE')
