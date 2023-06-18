#!/usr/bin/env bash
echo "Start web application"
exec gunicorn -c conf/gunicorn.conf.py --timeout 180
