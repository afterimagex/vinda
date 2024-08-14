#!/bin/bash

set -e

PROJECT_DIR=$(dirname $(realpath $0))


function docker_rmi() {
    if [[ "$(docker images -q $1 2> /dev/null)" != "" ]]; then
        echo "rm image $1"
        docker rmi $1
    fi
}


function build() {
    cd ${PROJECT_DIR}
    image_name="vinda:dev"
    echo "build image: ${image_name}"
    if [[ "$(docker images -q ${image_name} 2> /dev/null)" == "" ]]; then
        echo "镜像不存在: ${image_name}"
        docker build -t ${image_name} -f docker/Dockerfile.dev .
    fi
    docker run -it --rm -v ${PROJECT_DIR}:/work/vinda ${image_name} \
    bash -c "cd /work/vinda && rm -rf build dist && python setup.py bdist_wheel"
}


function build_base() {
    cd ${PROJECT_DIR}
    image_name="vinda:base"
    echo "build image: ${image_name}"
    # docker_rmi ${image_name}
    if [[ "$(docker images -q ${image_name} 2> /dev/null)" == "" ]]; then
        echo "镜像不存在: ${image_name}"
        docker build -t ${image_name} -f docker/Dockerfile.base .
    fi
}


function package() {
    cd ${PROJECT_DIR}
    image_name="vinda:prod"
    if [[ "$(docker images -q ${image_name} 2> /dev/null)" != "" ]]; then
        docker rmi ${image_name}
    fi
    # tar -cvf xxx.tar path/to/models-timm-xxxx/
    docker build --build-arg whlfile=./dist --build-arg modelfile=./data/mbv4.tar -t ${image_name} -f docker/Dockerfile.prod .
}


build
build_base
package