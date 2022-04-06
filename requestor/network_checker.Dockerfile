FROM python:3.8-slim
WORKDIR /network_checker/

RUN apt update \
    && apt install -y git gcc

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY erigolem_cli.py .
COPY gen_keystore.py .
RUN python3 ./gen_keystore.py

ENV PYTHONUNBUFFERED=1

CMD ["python3", "./erigolem_cli.py", "net-check"]
