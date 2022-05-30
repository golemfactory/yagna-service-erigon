import random
import string

from eth_account import Account
from eth_account.datastructures import HexBytes
from eth_account.messages import encode_defunct
from web3 import Web3

MESSAGE_FOR_VALIDATION = 'Confirm the terms of use of the application: {}'

def hash_personal_message(msg):
    padded = "\x19Ethereum Signed Message:\n" + str(len(msg)) + msg
    return sha3.keccak_256(bytes(padded, 'utf8')).digest()

def validate_massage(user_id: str, signature: HexBytes, original: str) -> bool:
    original_message = encode_defunct(Web3.toBytes(text=original))
    recover_user_address = Account.recover_message(original_message, signature=signature)

    return recover_user_address == user_id


def generate_message(code_len: int) -> str:
    code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(code_len))
    return MESSAGE_FOR_VALIDATION.format(code)
