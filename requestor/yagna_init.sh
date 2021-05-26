#!/bin/bash

set -m

/usr/bin/yagna service run &

sleep 5

/usr/bin/yagna app-key create requestor
/usr/bin/yagna payment fund --driver zksync
/usr/bin/yagna payment init --sender --driver zksync
