from os import environ as env

MESSAGE_VALIDATION = bool(env.get('EG_MESSAGE_VALIDATION', 'true'))
MESSAGE_FOR_VALIDATION = env.get('EG_MESSAGE_FOR_VALIDATION', 'Confirm the terms of use of the application: {}')

__all__ = [
    'MESSAGE_VALIDATION',
    'MESSAGE_FOR_VALIDATION'
]