from unittest import TestCase
from eth_account.messages import encode_defunct
from eth_account import Account
import requests

from requestor.server.utils import validate_massage


class MessageVerificationTestCase(TestCase):
    user_private_key: bytes = b"\xb2\\}\xb3\x1f\xee\xd9\x12''\xbf\t9\xdcv\x9a\x96VK-\xe4\xc4rm\x03[6\xec\xf1\xe5\xb3d"
    message: str = 'First Message'
    message2: str = 'Second Message'
    account: Account = Account()

    def test_correct_validation(self):
        message = encode_defunct(text=self.message)
        signed_message = self.account.sign_message(signable_message=message, private_key=self.user_private_key)
        self.assertTrue(validate_massage(
            '0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E',
            signed_message.signature,
            self.message
        ))

    def test_invalid_validation(self):
        message = encode_defunct(text=self.message2)
        signed_message = self.account.sign_message(signable_message=message, private_key=self.user_private_key)
        self.assertFalse(validate_massage(
            '0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E',
            signed_message.signature,
            self.message
        ))

    def test_api_correct_call(self):
        account = Account.create('TEST ACCOUNT')
        response = requests.get('http://localhost:8000/getMessage')
        message = response.json()
        encode_message = encode_defunct(text=message)
        signed_message = account.sign_message(signable_message=encode_message)
        self.assertTrue(validate_massage(
            account.address,
            signed_message.signature,
            message
        ))

    def test_api_incorrect_call(self):
        response = requests.post('http://localhost:8000/getMessage')
        self.assertTrue(response.status_code == 405)
