from yapapi import WorkContext
import json

def parse_result(raw_data):
    command_executed = raw_data[0]
    msg = command_executed.message
    msg = json.loads(msg)
    stdout = msg['stdout']
    mock_echo_data, erigon_data = stdout.split('ERIGON: ', 2)
    erigon_data = json.loads(erigon_data)
    return erigon_data


async def deploy(ctx, erigon):
    deployment_fut = await erigon.queue.get()

    #   NOTE: this is not necessary, but without any ctx.run() it seems that
    #   ctx.commit() does nothing and we would deploy only when first request for status
    ctx.run('STATUS')
    yield
    deployment_fut.set_result({'status': 'DEPLOYED'})


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

    async for _ in deploy(ctx, erigon):
        yield ctx.commit()

    async for requesting_future in process_commands(ctx, erigon):
        processing_future = yield ctx.commit()
        result = parse_result(processing_future.result())
        requesting_future.set_result(result)

    task.accept_result(result='DONE')
