#!/bin/bash

set -e


REMOTE_HOST="139.9.129.3"


ssh -S socket_8061 -O exit ${REMOTE_HOST}
ssh -S socket_8062 -O exit ${REMOTE_HOST}
ssh -S socket_8063 -O exit ${REMOTE_HOST}