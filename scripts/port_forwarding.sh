#!/bin/bash

set -e


REMOTE_HOST="139.9.129.3"


function get_option() {
    while getopts "hrs" OPTION; do
        case ${OPTION} in
            h)
                print_help
                exit 0
            ;;
            r)
                start_all
                exit 0
            ;;
            s)
                stop_all
                exit 0
            ;;
            *)
                echo -e "unknow option ${OPTION}" >&2
                exit 0
            ;;
        esac
    done
    echo -e "default" >&2
    return 0
}


function print_help() {
    echo -e "Usage: $0" >&2
    echo -e "   -h: print help message" >&2
    echo -e "   -r: start forwarding" >&2
    echo -e "   -s: stop forwarding" >&2
    return 0
}


function remote_forwarding() {
    # -C: 启用压缩
    # -N: 不执行远程命令
    # -g: 允许远程主机连接到本地转发的端口
    # -M: 使用master模式
    # -S: 指定一个控制socker的路径
    # -f: 后台运行
    ssh -CNMfg -S "rs_$1" -R 0.0.0.0:$1:localhost:$2 root@${REMOTE_HOST} -o ServerAliveInterval=5 -o ServerAliveCountMax=3
}


function stop_forwarding() {
    ssh -S $1 -O exit ${REMOTE_HOST}
}


function start_all() {
    remote_forwarding 8061 8081
    remote_forwarding 8062 6006
    remote_forwarding 8063 8501
}


function stop_all() {
    stop_forwarding "rs_8061"
    stop_forwarding "rs_8062"
    stop_forwarding "rs_8063"
}


function cleanup() {
    echo "clean up done."
}


function main() {
    trap cleanup SIGINT SIGTERM EXIT
    get_option $@
}


stop_all