#!/bin/bash

#   GENERAL NOTE
#   Here we start yagna and server app in the same Docker container.
#   This works & is pretty simple, but the recommended way of running this sort
#   of a system on Docker is to have different processes running in different containers,
#   connected e.g. with docker-compose, like here: https://github.com/golemfactory/galatea

#   1.  Start yagna in the background & wait until it starts
set -m

/usr/bin/yagna service run > yagna_requestor_log 2>&1 &

sleep 5

#   2.  Initialize yagna requestor and payments
/usr/bin/yagna app-key create requestor
/usr/bin/yagna payment fund --driver zksync
/usr/bin/yagna payment init --sender --driver zksync

#   3.  Set the environment for the server app
export YAGNA_APPKEY=$(yagna app-key list | tail -2 | head -1 | head -c53 | tail -c32)

#   4.  Start server (TODO: gunicorn run)
python3 server.py
