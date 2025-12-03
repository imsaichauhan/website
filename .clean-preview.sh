#!/bin/bash
# Clean stale Quarto session directories periodically
while true; do
    sleep 2
    find /home/theodore/progress/.quarto -type d -name "quarto-session-temp*" -mmin +5 -exec rm -rf {} + 2>/dev/null
done
