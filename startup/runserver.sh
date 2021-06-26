#!/bin/sh

echo 'Creating development environments, please wait ...'
sleep 1

echo 'Starting RabbitMQ Server'
chmod +x ./startup/rabbitmq.sh
open -a Terminal.app ./startup/rabbitmq.sh
sleep 5

echo 'Starting Celery Worker'
chmod +x ./startup/celery_worker.sh
open -a Terminal.app ./startup/celery_worker.sh
sleep 2

echo 'Starting Celery Beat'
chmod +x ./startup/celery_beat.sh
open -a Terminal.app ./startup/celery_beat.sh
sleep 2

echo 'Installing requirements and starting local server'
source ./env/bin/activate
pip install -r requirements.txt
python manage.py runserver


