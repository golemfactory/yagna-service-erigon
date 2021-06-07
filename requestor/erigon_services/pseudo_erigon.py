from yapapi.payload import vm
from yapapi.services import Service
import asyncio

URL = 'www.some.where/erigon:7987'
AUTH = {
    'user': 'SECRET_USER',
    'password': 'SECRET_PASSWORD',
}


class PseudoErigon(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = None
        self.auth = None

    @classmethod
    async def get_payload(cls):
        #   NOTE: this is a blender image
        #         (because every provider has it downloaded)
        return await vm.repo(
            image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
            min_mem_gib=0.5,
            min_storage_gib=2.0,
        )

    async def run(self):
        await asyncio.sleep(3)
        self.url, self.auth = URL, AUTH

        await asyncio.sleep(9999999999999999)
        yield
