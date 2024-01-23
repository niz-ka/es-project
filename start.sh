#!/usr/bin/env bash

docker start elasticsearch

# Wait for container
until curl 127.0.0.1:9200 2>/dev/null; do
    sleep 1
done

(cd app && flask run --debug)
