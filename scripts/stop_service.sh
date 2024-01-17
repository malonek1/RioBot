#!/bin/bash
echo "Stopping RioBot"
killall python3 || true
killall /usr/local/bin/python3.9 || true
