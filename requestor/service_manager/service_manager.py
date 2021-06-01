import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from .service_wrapper import ServiceWrapper
from .yapapi_connector import YapapiConnector

DEFAULT_EXECUTOR_CFG = {
    'budget': 1.0,
    'subnet_tag': 'ttt2',
    'event_consumer': log_summary(log_event_repr),
}


class ServiceManager():
    def __init__(self, executor_cfg={}):
        self.executor_cfg = DEFAULT_EXECUTOR_CFG.copy()
        self.executor_cfg.update(executor_cfg)

        self.yapapi_connector = None
        self.service_wrappers = []

        enable_default_logger(log_file='log.log')

    def create_service(self, service_cls):
        self._init_yapapi_connector(service_cls)
        service_wrapper = ServiceWrapper()
        self.yapapi_connector.create_instance(service_wrapper)
        self.service_wrappers.append(service_wrapper)
        return service_wrapper

    def _init_yapapi_connector(self, service_cls):
        if self.yapapi_connector is None:
            self.yapapi_connector = YapapiConnector(service_cls, self.executor_cfg)

    async def close(self):
        tasks = [service_wrapper.stop() for service_wrapper in self.service_wrappers]
        await asyncio.gather(*tasks)

        if self.yapapi_connector is not None:
            await self.yapapi_connector.stop()
