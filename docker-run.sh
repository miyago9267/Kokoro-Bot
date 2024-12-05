#!/bin/bash
user="kokoro"
name="kokoro-bot"

docker build \
    $@ -t $user/$name:latest . || exit
[ "$(docker ps | grep $name)" ] && docker kill $name
[ "$(docker ps -a | grep $name)" ] && docker rm $name

docker run \
	-itd \
	-u $(id -u):$(id -g) \
	--name $name \
    --network host \
	--restart=always \
	--volume ./config:/app/config/ \
	$user/$name:latest