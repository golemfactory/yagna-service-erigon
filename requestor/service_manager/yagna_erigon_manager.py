import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from datetime import timedelta

DEFAULT_EXECUTOR_CFG = {
    'max_workers': 100,
    'budget': 1.0,
    'timeout': timedelta(minutes=30),
    'subnet_tag': 'ttt2',
    'event_consumer': log_summary(log_event_repr),
}


class YagnaErigonManager():
    def __init__(self, manager_cls, executor_cfg={}):
        self.manager_cls = manager_cls
        self.executor_cfg = DEFAULT_EXECUTOR_CFG.copy()
        self.executor_cfg.update(executor_cfg)

        enable_default_logger(log_file='log.log')
        self.manager = None
        self.erigons = []

    def create_erigon(self, service_cls):
        self._init_manager(service_cls)
        erigon = self.manager.add_instance()
        self.erigons.append(erigon)
        return erigon

    def _init_manager(self, service_cls):
        #   TODO: maybe - different manager per each service class
        #         (not needed for the Beta2 but maybe a nice feature?)
        if self.manager is None:
            self.manager = self.manager_cls(service_cls, self.executor_cfg)
        else:
            assert self.manager.service_cls == service_cls, "Attempt to create different services"

    async def close(self):
        tasks = [erigon.stop() for erigon in self.erigons]
        if self.manager is not None:
            tasks.append(self.manager.stop())

        await asyncio.gather(*tasks)
