#!/bin/bash

cat <<EOF | clickhouse client -mn

CREATE DATABASE IF NOT EXISTS shard;

CREATE TABLE IF NOT EXISTS shard.movie_watch_events
(
    user_id UUID,
    movie_id UUID,
    progress Float32,
    event_time DateTime
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/movie_watch_events', 'replica_1') PARTITION BY toYYYYMMDD(event_time) ORDER BY (user_id, movie_id, event_time);

CREATE TABLE IF NOT EXISTS default.movie_watch_events
(
    user_id UUID,
    movie_id UUID,
    progress Float32,
    event_time DateTime
) ENGINE = Distributed('company_cluster', '', movie_watch_events, rand());

CREATE TABLE IF NOT EXISTS default.kafka_table
(
    user_id UUID,
    movie_id UUID,
    progress Float32,
    event_time DateTime
) ENGINE = Kafka
SETTINGS
    kafka_broker_list = '${KAFKA_BROKER}',
    kafka_topic_list = '${KAFKA_TOPIC}',
    kafka_group_name = '${KAFKA_GROUP_NAME}',
    kafka_format = '${KAFKA_FORMAT}';

CREATE MATERIALIZED VIEW IF NOT EXISTS kafka_mv TO default.movie_watch_events AS
SELECT * FROM default.kafka_table;
EOF
