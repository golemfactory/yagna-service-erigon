#!/usr/bin/env python3

import json
import logging
import threading
import time
import urllib.parse as urlparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

import click
import click_logging  # type: ignore
import requests
import web3.providers
from pydantic import BaseModel, HttpUrl
from requests import RequestException
from requests.auth import HTTPBasicAuth
from web3.auto import w3

if TYPE_CHECKING:
    from typing import TextIO, Any

logger = logging.getLogger()
click_logging.basic_config(logger)

DEFAULT_INIT_PARAMS = json.dumps({
    "name": "My Node",
    "params": {
        "network": "goerli"
    }
})


class Status(str, Enum):
    pending = 'pending'
    starting = 'starting'
    running = 'running'
    stopping = 'stopping'
    stopped = 'stopped'
    failed = 'failed'


class Credentials(BaseModel):
    user: str
    password: str


class Instance(BaseModel):
    id: str
    name: str
    init_params: dict
    status: Status

    url: Optional[HttpUrl]
    auth: Optional[Credentials]
    network: Optional[str]

    created_at: datetime
    stopped_at: Optional[datetime]

    @property
    def is_active(self) -> bool:
        return self.status in (Status.pending, Status.starting, Status.running)


class InstanceList(BaseModel):
    __root__: List[Instance]


class ErigolemClient:
    # That's no mistake: threading.local() should be called once, not per thread
    _thread_data = threading.local()

    def __init__(self, erigolem_url: str, keystore: 'TextIO', password: str):
        if not erigolem_url.endswith('/'):
            erigolem_url += '/'
        self._erigolem_url = erigolem_url
        private_key = w3.eth.account.decrypt(keystore.read(), password)
        self._account = w3.eth.account.from_key(private_key)

    @property
    def _session(self) -> requests.Session:
        # Each thread should have its own session because requests.Session is not thread-safe
        # See https://github.com/psf/requests/issues/2766 for details
        if not hasattr(self._thread_data, 'session'):
            self._thread_data.session = requests.Session()
            self._thread_data.session.headers.update(
                {'Authorization': f'Bearer {self._account.address}'})
        return self._thread_data.session

    def _get(self, url: str) -> 'Any':
        url = urlparse.urljoin(self._erigolem_url, url)
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()

    def _post(self, url: str, data: 'Optional[Any]' = None) -> 'Any':
        url = urlparse.urljoin(self._erigolem_url, url)
        response = self._session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_instances(self) -> 'List[Instance]':
        return [Instance(**d) for d in self._get('getInstances')]

    def create_instance(self, params: dict) -> Instance:
        return Instance(**self._post('createInstance', data=params))

    def stop_instance(self, instance_id: str) -> Instance:
        return Instance(**self._post(f'stopInstance/{instance_id}'))


class NetworkChecker:
    def __init__(
            self,
            client: ErigolemClient,
            num_instances: int,
            pending_timeout_sec: int,
            check_interval_sec: int,
            init_params: dict,
    ):
        self._client = client
        self._num_instances = num_instances
        self._pending_timeout = timedelta(seconds=pending_timeout_sec)
        self._check_interval_sec = check_interval_sec
        self._init_params = init_params
        self._executor = ThreadPoolExecutor()
        self._shutdown = False

    def _get_active_instances(self) -> 'List[Instance]':
        return [i for i in self._client.get_instances() if i.is_active]

    def _stop_instance(self, instance: Instance) -> None:
        logger.info('Stopping instance %s ...', instance.id)
        self._client.stop_instance(instance.id)
        logger.info('Instance %s stopped.', instance.id)

    def _create_instance(self) -> None:
        logger.info('Creating new instance...')
        instance = self._client.create_instance(self._init_params)
        logger.info('Instance %s created', instance.id)

    def _recreate_instance(self, instance: Instance) -> None:
        logger.info('Instance %s is stale and will be recreated', instance.id)
        self._stop_instance(instance)
        self._create_instance()

    @staticmethod
    def _check_web3_provider(provider_url: HttpUrl, credentials: Credentials) -> None:
        provider = web3.providers.HTTPProvider(provider_url, request_kwargs={
            'auth': HTTPBasicAuth(credentials.user, credentials.password)
        })
        w3 = web3.Web3(provider)
        block = w3.eth.get_block_number()
        logger.debug('Block: %s', block)
        assert isinstance(block, int)

    def _check_instance(self, instance: Instance) -> None:
        try:
            assert instance.url is not None
            assert instance.auth is not None
            self._check_web3_provider(instance.url, instance.auth)
        except (AssertionError, RequestException):
            self._recreate_instance(instance)

    def _check(self) -> None:
        if self._shutdown:
            logger.info('Network checker in shutdown. Skipping check')
            return

        logger.info('Starting network check...')
        active_instances = self._get_active_instances()
        logger.info('Active instances: %d / %d', len(active_instances), self._num_instances)

        # Create new instances if necessary
        num_new_instances = self._num_instances - len(active_instances)
        if num_new_instances > 0:
            logger.info('Creating %d new instances...', num_new_instances)
            self._executor.map(lambda _: self._create_instance(), range(num_new_instances))
            logger.info('Finished creating new instances')

        stale_threshold = datetime.utcnow() - self._pending_timeout

        # Check if started instances are running and responsive
        def check_active_instance(instance):
            if instance.status is Status.running:
                self._check_instance(instance)
            elif instance.created_at < stale_threshold:
                self._recreate_instance(instance)
        self._executor.map(check_active_instance, active_instances)

        logger.info('Network check done')

    def _stop(self) -> None:
        logger.info('Shutting down network checker...')
        self._shutdown = True
        self._executor.map(self._stop_instance, self._get_active_instances())
        self._executor.shutdown()
        logger.info('Network checker shutdown complete')

    def run(self):
        while True:
            try:
                self._check()
                time.sleep(self._check_interval_sec)
            except KeyboardInterrupt:
                self._stop()
                return
            except Exception:  # pylint: disable=too-broad-except
                logger.exception('Network check error')
                continue


@click.group()
@click_logging.simple_verbosity_option(logger, '-l', '--log-level')
@click.option('--erigolem-url', default='http://localhost:5000/', envvar='ERIGOLEM_URL')
@click.option('--keystore', type=click.File(), default='keystore.json', envvar='KEYSTORE')
@click.option('--password', default='', envvar='PASSWORD')
@click.pass_context
def cli(ctx, erigolem_url, keystore, password):
    ctx.obj = ErigolemClient(erigolem_url, keystore, password)


@cli.command(name='list')
@click.option('--active-only', is_flag=True)
@click.pass_obj
def get_instances(client: ErigolemClient, active_only: bool):
    instances = client.get_instances()
    if active_only:
        instances = [i for i in instances if i.is_active]
    click.echo(InstanceList(__root__=instances).json())


@cli.command(name='create')
@click.argument('params')
@click.pass_obj
def create_instance(client: ErigolemClient, params: str):
    params_dict = json.loads(params)
    instance = client.create_instance(params_dict)
    click.echo(instance.json())


@cli.command(name='stop')
@click.argument('instance_id')
@click.pass_obj
def stop_instance(client: ErigolemClient, instance_id: str):
    instance = client.stop_instance(instance_id)
    click.echo(instance.json())


@cli.command(name='net-check')
@click.option('--num-instances', type=click.INT, default=10, envvar='NUM_INSTANCES')
@click.option('--pending-timeout-sec', type=click.INT, default=60, envvar='PENDING_TIMEOUT_SEC')
@click.option('--check-interval-sec', type=click.INT, default=60, envvar='CHECK_INTERVAL_SEC')
@click.option('--init-params', default=DEFAULT_INIT_PARAMS, envvar='INIT_PARAMS')
@click.pass_obj
def net_check(
        client: ErigolemClient,
        num_instances: int,
        pending_timeout_sec: int,
        check_interval_sec: int,
        init_params: str
):
    checker = NetworkChecker(
        client=client,
        num_instances=num_instances,
        pending_timeout_sec=pending_timeout_sec,
        check_interval_sec=check_interval_sec,
        init_params=json.loads(init_params)
    )
    checker.run()


if __name__ == '__main__':
    cli()
