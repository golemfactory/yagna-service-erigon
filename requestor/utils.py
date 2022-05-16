import random
import string

from eth_account import Account
from eth_account.datastructures import SignedMessage
from eth_account.messages import encode_defunct
from web3 import Web3

MESSAGE_FOR_VALIDATION = 'Confirm the terms of use of the application: {}'


def validate_massage(user_id: str, message: SignedMessage, original: str) -> bool:
    original_message = encode_defunct(Web3.toBytes(text=original))
    recover_user_address = Account.recover_message(original_message, signature=message.signature)
    return recover_user_address == user_id


def generate_message(code_len: int) -> str:
    code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(code_len))
    return MESSAGE_FOR_VALIDATION.format(code)
