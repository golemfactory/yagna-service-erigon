FROM python:3.8
WORKDIR /erigon_server_test/

RUN pip install pytest==6.2.3 requests==2.25.1 pytest-asyncio==0.15.1 httpx==0.18.1

COPY tests tests

ENTRYPOINT ["pytest", "-s", "-v"]
