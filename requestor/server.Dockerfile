FROM python:3.8
WORKDIR /erigon_server/

#   Install yagna
#   NOTE: ARG instead of ENV because I don't want this in the final image
ARG DEBIAN_FRONTEND=noninteractive

ADD https://github.com/golemfactory/yagna/releases/download/pre-rel-v0.6.6-rc1/golem-requestor_pre-rel-v0.6.6-rc1_amd64.deb yagna.deb
RUN dpkg-preconfigure ./yagna.deb
RUN echo "golem-requestor	golem/terms/testnet-01	select	yes" | debconf-set-selections
RUN apt install -y ./yagna.deb

#   Install certificates
RUN apt update \
    && apt install -y libssl-dev ca-certificates \
    && update-ca-certificates

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

#   Cleanup
RUN rm yagna.deb requirements.txt

#   Replace yapapi with the non-released version
#   (All those lines should disappear with new yapapi version in requirements.txt)
RUN pip3 uninstall -y yapapi
RUN apt-get install -y git
RUN git clone https://github.com/golemfactory/yapapi.git yapapi_repo
#   services api is now in master
# RUN cd yapapi_repo; git checkout johny-b/blue-services-api-static
RUN python3 -m pip install deprecated==1.2.12 python-statemachine==0.8.0

COPY yagna_init.sh .
RUN chmod +x yagna_init.sh

COPY server.py       .
COPY service_manager service_manager
COPY static          static

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["bash", "-c", "         \
                ./yagna_init.sh;    \
                YAGNA_APPKEY=$(yagna app-key list | tail -2 | head -1 | head -c53 | tail -c32) \
                PYTHONPATH=yapapi_repo:$PYTHONPATH \
                    python3 server.py"  ]
