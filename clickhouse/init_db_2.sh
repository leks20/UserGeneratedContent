#!/bin/bash

cat <<EOF | clickhouse client -mn

CREATE DATABASE IF NOT EXISTS replica;
CREATE TABLE IF NOT EXISTS replica.movie_watch_events
(
    user_id UUID,
    movie_id UUID,
    progress Float32,
    event_time DateTime
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movie_watch_events', 'replica_2') PARTITION BY toYYYYMMDD(event_time) ORDER BY (user_id, movie_id, event_time);
EOF
