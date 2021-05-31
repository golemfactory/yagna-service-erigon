import uuid


class ServiceWrapper():
    def __init__(self):
        self.id = self._create_id()
        self.stopped = False
        self.service = None

    def set_service(self, service):
        self.service = service

    @property
    def started(self):
        return self.service is not None

    async def stop(self):
        if self.stopped:
            return

        self.disable()
        if self.started:
            return await self.run_single_command('STOP')
        else:
            return "not started yet"

    def disable(self):
        if self.stopped:
            return
        self.stopped = True
        print(f"STOPPING {self}")

    async def run_single_command(self, cmd):
        self.service.send_message_nowait(cmd)
        service_signal = await self.service.receive_message()
        #   TODO: how do we check if we got response for the signal sent?
        #         this is irrelevant now, but could be useful in the future
        return service_signal.message

    def _create_id(self):
        return uuid.uuid4().hex

    def __repr__(self):
        return f"{type(self).__name__}[id={self.id}]"
