#!/bin/bash

set -e


REMOTE_HOST="139.9.129.3"


ssh -CfNg -M -S socket_8061 -R 0.0.0.0:8061:localhost:8081 root@${REMOTE_HOST} -o TCPKeepAlive=true ServerAliveInterval=5
ssh -CfNg -M -S socket_8062 -R 0.0.0.0:8062:localhost:6006 root@${REMOTE_HOST} -o TCPKeepAlive=true ServerAliveInterval=5
ssh -CfNg -M -S socket_8063 -R 0.0.0.0:8063:localhost:8501 root@${REMOTE_HOST} -o TCPKeepAlive=true ServerAliveInterval=5
