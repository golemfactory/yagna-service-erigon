from unittest import TestCase
from eth_account.messages import encode_defunct
from eth_account import Account
from requestor.utils import validate_massage


class MessageVerificationTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user_private_key: bytes = b"\xb2\\}\xb3\x1f\xee\xd9\x12''\xbf\t9\xdcv\x9a\x96VK-\xe4\xc4rm\x03[6\xec\xf1\xe5\xb3d"
        cls.message: str = 'First Message'
        cls.message2: str = 'Second Message'

    def test_correct_validation(self):
        message = encode_defunct(text=self.message)
        signed_message = Account.sign_message(message, private_key=self.user_private_key)
        self.assertTrue(validate_massage('0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E', signed_message, self.message))

    def test_invalid_validation(self):
        message = encode_defunct(text=self.message2)
        signed_message = Account.sign_message(message, private_key=self.user_private_key)
        self.assertFalse(validate_massage('0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E', signed_message, self.message))
