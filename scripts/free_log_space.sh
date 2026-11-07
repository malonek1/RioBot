#!/bin/bash
# The pre-rotation deploy wrote one unbounded /var/log/riobot.log; a log flood
# grew it until the disk was full. Empty it if it's over the rotation cap.
LOG=/var/log/riobot.log
if [ -f "$LOG" ] && [ "$(du -m "$LOG" | cut -f1)" -gt 100 ]; then
    echo "Emptying oversized $LOG"
    truncate -s 0 "$LOG"
fi
