import string
import random

MESSAGE_FOR_VALIDATION = 'Confirm the terms of use of the application: {}'


def generate_message(code_len: int) -> str:
    code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(code_len))
    return MESSAGE_FOR_VALIDATION.format(code)
