#!/bin/bash

while /usr/bin/true 
do  
    curl -s http://admin:password@192.168.1.3/gett1.cgi >> temp.log;
    date +"|%d-%m-%y-%H:%M:%S" >> temp.log 
    sleep 1
done

