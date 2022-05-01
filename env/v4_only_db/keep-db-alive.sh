#!/usr/bin/env bash

while true;
do
    usage=$(free -t | awk 'NR == 2 {printf("%d", $3/$2*100)}');
    if [[ usage -gt 90 ]];
    then
        sudo service mysql stop;
        sudo service mysql start;
    fi
    sleep 1;
done
