#!/bin/sh

# enter current directory
cd ~Desktop/mirapayments


# start rabbitmq
export PATH=$PATH:/usr/local/sbin

rabbitmq-server

read