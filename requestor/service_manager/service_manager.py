import asyncio
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from .service_wrapper import ServiceWrapper
from .yapapi_connector import YapapiConnector
from functools import partial

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, List, Any
    from yapapi.executor.services import Service


DEFAULT_EXECUTOR_CFG = {
    'budget': 1.0,
    'subnet_tag': 'erigon',
    'event_consumer': log_summary(log_event_repr),
}


async def stop_on_golem_exception(service_manager, e):
    print("GOLEM FAILED\n", e)
    print("STOPPING THE LOOP")
    loop = asyncio.get_event_loop()
    loop.stop()


async def restart_on_golem_exception(service_manager, e):
    pass


class ServiceManager():
    def __init__(self, user_executor_cfg={}, golem_exception_handler='stop'):
        self.executor_cfg = DEFAULT_EXECUTOR_CFG.copy()
        self.executor_cfg.update(user_executor_cfg)
        self.golem_exception_handler = golem_exception_handler

        enable_default_logger(log_file='log.log')

        self._start()

        import os
        os.environ['YAGNA_APPKEY'] = 'a'

    def create_service(self, service_cls: 'Type[Service]', start_args: 'List[Any]' = []):
        service_wrapper = ServiceWrapper(service_cls, start_args)
        self.yapapi_connector.create_instance(service_wrapper)
        self.service_wrappers.append(service_wrapper)
        return service_wrapper

    async def close(self):
        for service_wrapper in self.service_wrappers:
            service_wrapper.stop()
        await self.yapapi_connector.stop()

    def _start(self):
        self.service_wrappers = []
        exception_handler = self._prepare_exception_handler()
        self.yapapi_connector = YapapiConnector(self.executor_cfg, exception_handler)

    def _prepare_exception_handler(self):
        handler_func = self._parse_handler_param()
        return partial(handler_func, self)

    def _parse_handler_param(self):
        handler_param = self.golem_exception_handler

        if handler_param == 'stop':
            return stop_on_golem_exception
        elif handler_param == 'restart':
            return restart_on_golem_exception
        elif callable(handler_param):
            return handler_param
        else:
            raise ValueError("golem_exception_handler should be either 'start' or 'restart' or a callable")
