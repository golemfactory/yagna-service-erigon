#!/usr/bin/env python3

import json

import click
from web3.auto import w3


@click.command()
@click.option('--keystore', type=click.File(mode='w'), default='keystore.json', envvar='KEYSTORE')
@click.option('--password', default='', envvar='PASSWORD')
def generate_keystore(keystore, password):
    account = w3.eth.account.create()
    encrypted = account.encrypt(password=password)
    json.dump(encrypted, keystore)


if __name__ == '__main__':
    generate_keystore()
