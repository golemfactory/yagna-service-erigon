FROM python:3.8
WORKDIR /erigon_server_test/

RUN pip install pytest==6.2.3 requests==2.25.1

COPY tests tests

ENTRYPOINT pytest
