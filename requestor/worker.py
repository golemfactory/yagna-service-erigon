from yapapi import WorkContext
import json


def parse_result(raw_data):
    command_executed = raw_data[0]
    stdout = command_executed.stdout
    mock_echo_data, erigon_data = stdout.split('ERIGON: ', 2)
    erigon_data = json.loads(erigon_data)
    return erigon_data


async def process_commands(ctx, erigon):
    queue = erigon.queue
    while True:
        command, requesting_future = await queue.get()
        if command == 'STATUS':
            ctx.run(command)
            yield requesting_future
        elif command == 'STOP':
            requesting_future.set_result({'status': 'STOPPING'})
            break


async def worker(ctx: WorkContext, tasks):
    task = await tasks.__anext__()
    erigon = task.data

    if erigon.stopped:
        task.accept_result(result='This erigon was stopped before deployment')
        return

    #   DEPLOYMENT
    deployment_fut = await erigon.queue.get()
    try:
        #   NOTE: this is not necessary, but without any ctx.run() it seems that
        #   ctx.commit() does nothing and we would deploy only when first status
        #   request comes
        ctx.run('STATUS')
        yield ctx.commit()
    except Exception as e:
        print("DEPLOYMENT FAILED ", e)
        #   Put the deployment_fut back to queue so when this function
        #   restarts we'll be in the same state
        erigon.queue.put_nowait(deployment_fut)
        task.reject_result(retry=True)
        return

    #   We got here -> deployment succeeded
    deployment_fut.set_result({'status': 'DEPLOYED'})

    #   REQUEST PROCESSING
    async for requesting_future in process_commands(ctx, erigon):
        processing_future = yield ctx.commit()
        result = parse_result(processing_future.result())
        requesting_future.set_result(result)

    task.accept_result(result='DONE')
