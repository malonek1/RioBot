#!/bin/bash
echo "Running RioBot"
cd /home/ec2-user/RioBot/main
nohup RioBot.py 1>/dev/null 2>/dev/null &