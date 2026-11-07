#!/bin/bash
echo "Running RioBot"
cd /home/ec2-user/RioBot/main
# The bot logs to a rotating /var/log/riobot.log itself (see RioBot.py); the
# console file only catches what bypasses logging, e.g. a crash at import.
RIOBOT_LOG_FILE=/var/log/riobot.log nohup python3.11 RioBot.py > /var/log/riobot-console.log 2>&1 &
