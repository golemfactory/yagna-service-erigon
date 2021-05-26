#!/bin/bash

set -m

/usr/bin/yagna service run > yagna_requestor_log 2>1 &

sleep 5

/usr/bin/yagna app-key create requestor
/usr/bin/yagna payment fund --driver zksync
/usr/bin/yagna payment init --sender --driver zksync
