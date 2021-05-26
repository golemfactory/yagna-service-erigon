FROM ubuntu
WORKDIR erigon_server
    
#   Install python
RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install python3.8 python3-distutils

#   And pip
ADD https://bootstrap.pypa.io/get-pip.py get-pip.py
RUN python3 get-pip.py

#   Install yagna & certificates
ADD https://github.com/golemfactory/yagna/releases/download/pre-rel-v0.6.6-rc1/golem-requestor_pre-rel-v0.6.6-rc1_amd64.deb yagna.deb
RUN yes | apt install -y ./yagna.deb \
    && apt install -y libssl-dev ca-certificates \
    && update-ca-certificates

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

#   Replace yapapi with the non-released version
RUN pip3 uninstall -y yapapi
RUN apt-get install -y git
RUN git clone https://github.com/golemfactory/yapapi.git yapapi_repo
RUN cd yapapi_repo; git checkout az/smarter-smart-queue
RUN python3 -m pip install deprecated==1.2.12

COPY yagna_init.sh .
RUN chmod +x yagna_init.sh

COPY services                services
COPY server.py               server.py
COPY yagna_erigon_manager.py yagna_erigon_manager.py
COPY worker.py               worker.py

ENTRYPOINT ["bash", "-c", "         \
                ./yagna_init.sh;    \
                YAGNA_APPKEY=$(yagna app-key list | tail -2 | head -1 | head -c53 | tail -c32) \
                PYTHONPATH=yapapi_repo:$PYTHONPATH \
                    python3 server.py"  ]
