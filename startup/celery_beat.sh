#!/bin/sh

cd ~/Desktop/mirapayments

# activate env
source ./env/bin/activate

# start celery beat
celery -A mirapayments beat -l info

read