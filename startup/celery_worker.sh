#!/bin/sh

cd ~/Desktop/mirapayments

# activate env
source ./env/bin/activate

# start celery worker
celery -A mirapayments worker -l info

read