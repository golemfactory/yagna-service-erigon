import json
import typing
import urllib.parse as urlparse

import click
import requests
from web3.auto import w3

if typing.TYPE_CHECKING:
    from typing import TextIO, Optional, Any


class ErigolemClient:
    def __init__(self, erigolem_url: str, keystore: 'TextIO', password: str):
        if not erigolem_url.endswith('/'):
            erigolem_url += '/'
        self._erigolem_url = erigolem_url
        private_key = w3.eth.account.decrypt(keystore.read(), password)
        self._account = w3.eth.account.from_key(private_key)
        self._session = requests.Session()
        self._session.headers.update({'Authorization': f'Bearer {self._account.address}'})

    def _get(self, url: str) -> dict:
        url = urlparse.urljoin(self._erigolem_url, url)
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()

    def _post(self, url: str, data: 'Optional[Any]' = None) -> dict:
        url = urlparse.urljoin(self._erigolem_url, url)
        response = self._session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_instances(self) -> 'dict[str, dict]':
        return self._get('getInstances')

    def create_instance(self, params: dict) -> dict:
        return self._post('createInstance', data=params)

    def stop_instance(self, instance_id: str) -> dict:
        return self._post(f'stopInstance/{instance_id}')


@click.group()
@click.option('--erigolem-url', default='http://localhost:5000/', envvar='ERIGOLEM_URL')
@click.option('--keystore', type=click.File(), envvar='KEYSTORE')
@click.option('--password', envvar='PASSWORD')
@click.pass_context
def cli(ctx, erigolem_url, keystore, password):
    ctx.obj = ErigolemClient(erigolem_url, keystore, password)


@cli.command(name='list')
@click.pass_obj
def get_instances(client: ErigolemClient):
    instances = client.get_instances()
    click.echo(instances)


@cli.command(name='create')
@click.argument('params')
@click.pass_obj
def create_instance(client: ErigolemClient, params: str):
    params_dict = json.loads(params)
    instance = client.create_instance(params_dict)
    click.echo(instance)


@cli.command(name='stop')
@click.argument('instance_id')
@click.pass_obj
def stop_instance(client: ErigolemClient, instance_id: str):
    instance = client.stop_instance(instance_id)
    click.echo(instance)


if __name__ == '__main__':
    cli()
