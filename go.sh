#!/bin/bash -xe

docker run \
  --name neo4j \
  -d --rm \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/logs:/logs \
  -v $HOME/neo4j/import:/import \
  -v $HOME/neo4j/plugins:/plugins \
  neo4j:latest
docker run -p 6333:6333 -p 6334:6334 \
  -d --rm \
  -v $HOME/qdrant/storage:/qdrant/storage \
  qdrant/qdrant
