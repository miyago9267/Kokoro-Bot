#!/bin/bash
user="kokoro"
name="kkr_mora_bot"

if [ command -v poetry &> /dev/null ]; then
    poetry export --without_hashes > requirements.txt
else
    echo "Poetry not found. Using requirements.txt"
    exit
fi

docker build \
    $@ -t $user/$name:latest . || exit
[ "$(docker ps | grep $name)" ] && docker kill $name
[ "$(docker ps -a | grep $name)" ] && docker rm $name

docker run \
	-itd \
	-u $(id -u):$(id -g) \
	--name $name \
    --network host \
	$user/$name:latest