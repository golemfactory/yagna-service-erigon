import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, List, Any, Optional
    from yapapi.services import Service, Cluster


class ServiceWrapper():
    def __init__(self, service_cls: 'Type[Service]', start_args: 'List[Any]'):
        self.service_cls = service_cls
        self.start_args = start_args
        self.id = self._create_id()
        self.stopped = False
        self._cluster: 'Optional[Cluster]' = None

    @property
    def cluster(self):
        return self._cluster

    @property
    def service(self):
        if self._cluster and self._cluster.instances:
            return self._cluster.instances[0]
        return None

    @property
    def started(self):
        return self.service is not None

    @cluster.setter
    def cluster(self, cluster: 'Cluster'):
        #   TODO: change to a public attribute when it is available in yapapi
        #         (this is already requested, issue 459)
        if cluster._service_class != self.service_cls:
            raise ValueError(f"Expected: {self.service_cls.__name__}, got {cluster._service_class.__name__}")

        if self.stopped:
            #   This is a very-rare-but-possible situation when we got stopped before the cluster
            #   was created --> cluster has to be stopped as well
            cluster.stop()

        self._cluster = cluster

    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        print(f"STOPPING {self}")

        if self.cluster is not None:
            self.cluster.stop()

    async def run_single_command(self, cmd: str):
        self.service.send_message_nowait(cmd)
        service_signal = await self.service.receive_message()
        #   TODO: how do we check if we got response for the signal sent?
        #         this is irrelevant now, but could be useful in the future
        return service_signal.message

    def _create_id(self):
        return uuid.uuid4().hex

    def __repr__(self):
        name = self.service_cls.__name__
        return f"{name}[id={self.id}]"
