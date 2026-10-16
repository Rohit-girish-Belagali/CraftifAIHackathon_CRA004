#!/usr/bin/env bash
# Usage: ./run.sh file:///home/user/videos/site.mp4 [mqtt-broker-host]
set -e
python3 -m sentinel.deepstream_app --uri "$1" ${2:+--broker "$2"}
