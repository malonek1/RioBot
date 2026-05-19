#!/bin/bash
echo "Running RioBot"
cd /home/ec2-user/RioBot/main
sudo nohup python3.11 RioBot.py > /var/log/riobot.log 2>&1 &