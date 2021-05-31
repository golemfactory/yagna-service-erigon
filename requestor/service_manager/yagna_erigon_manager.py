import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from .service_wrapper import ServiceWrapper
from .yapapi_connector import YapapiConnector

#   NOTE: those are thigs common for Executor/Golem. Other things are hardcoded.
DEFAULT_EXECUTOR_CFG = {
    'budget': 1.0,
    'subnet_tag': 'ttt2',
    'event_consumer': log_summary(log_event_repr),
}


class YagnaErigonManager():
    def __init__(self, executor_cfg={}):
        self.executor_cfg = DEFAULT_EXECUTOR_CFG.copy()
        self.executor_cfg.update(executor_cfg)

        enable_default_logger(log_file='log.log')
        self.manager = None
        self.erigons = []

    def create_erigon(self, service_cls):
        self._init_manager(service_cls)
        erigon = ServiceWrapper()
        self.manager.add_instance(erigon)
        self.erigons.append(erigon)
        return erigon

    def _init_manager(self, service_cls):
        #   TODO: create different managers for different service classes
        if self.manager is None:
            self.manager = YapapiConnector(service_cls, self.executor_cfg)

    async def close(self):
        tasks = [erigon.stop() for erigon in self.erigons]
        await asyncio.gather(*tasks)

        if self.manager is not None:
            await self.manager.stop()
