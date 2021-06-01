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
    def __init__(self, user_executor_cfg={}):
        executor_cfg = DEFAULT_EXECUTOR_CFG.copy()
        executor_cfg.update(user_executor_cfg)

        self.yapapi_connector = YapapiConnector(executor_cfg)
        self.service_wrappers = []

        enable_default_logger(log_file='log.log')

    def create_service(self, service_cls):
        service_wrapper = ServiceWrapper()
        self.yapapi_connector.create_instance(service_wrapper, service_cls)
        self.service_wrappers.append(service_wrapper)
        return service_wrapper

    async def close(self):
        tasks = [service_wrapper.stop() for service_wrapper in self.service_wrappers]
        await asyncio.gather(*tasks)
        await self.yapapi_connector.stop()
