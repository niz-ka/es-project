#!/usr/bin/env bash

docker rm -f elasticsearch
rm -rf ./elastic-data
mkdir ./elastic-data
chmod 777 -R ./elastic-data

docker build . --tag elasticsearch:local

docker create -p 9200:9200 --name elasticsearch \
  -v ./elastic-data:/usr/share/elasticsearch/data \
  -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "xpack.security.http.ssl.enabled=false" \
  -e "xpack.license.self_generated.type=trial" \
  elasticsearch:local

docker start elasticsearch

sleep 60

curl -X PUT "localhost:9200/_ingest/pipeline/attachment?pretty" -H 'Content-Type: application/json' -d'
{
  "description" : "Extract attachment information",
  "processors" : [
    {
      "attachment" : {
        "field" : "data",
        "remove_binary": true
      }
    }
  ]
}
'

curl -X PUT localhost:9200/my-index-000001 -H 'Content-Type: application/json' -d '
{
"settings": {
    "analysis": {
      "analyzer": {
        "lang_pl": { 
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "morfologik_stem",
            "polish_stop"
          ]
        }
      }
    }
  }
}
'

docker stop elasticsearch
