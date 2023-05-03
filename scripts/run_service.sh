#!/bin/bash
echo "Running RioBot"
cd /home/ec2-user/RioBot/main
nohup python3.9 RioBot.py 1>/dev/null 2>/dev/null &