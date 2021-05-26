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
    try:
        async for set_success, set_failure in erigon.process_commands(ctx):
            processing_future = yield ctx.commit()
            set_success(processing_future)
    except Exception as e:
        print("COMMAND FAILED", e)
        erigon.disable()
        set_failure()

    task.accept_result(result='DONE')
