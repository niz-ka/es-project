FROM docker.elastic.co/elasticsearch/elasticsearch:8.11.3

RUN bin/elasticsearch-plugin install --batch analysis-stempel
RUN bin/elasticsearch-plugin install pl.allegro.tech.elasticsearch.plugin:elasticsearch-analysis-morfologik:8.11.3
