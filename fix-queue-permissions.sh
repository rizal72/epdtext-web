#!/bin/bash
# Fix permissions for epdtext IPC message queue
# This script ensures the pi user can access the message queue

QUEUE_FILE="/dev/mqueue/epdtext_ipc"
MAX_RETRIES=10
RETRY_DELAY=1

# Wait for queue to be created
for i in $(seq 1 $MAX_RETRIES); do
    if [ -e "$QUEUE_FILE" ]; then
        # Set permissions: owner=rw, group=rw, others=none
        chmod 660 "$QUEUE_FILE"
        # Change group to pi so pi user can access it
        chgrp pi "$QUEUE_FILE"
        echo "Queue permissions fixed: $(ls -l $QUEUE_FILE)"
        exit 0
    fi
    echo "Waiting for queue to be created... (attempt $i/$MAX_RETRIES)"
    sleep $RETRY_DELAY
done

echo "Error: Queue file not found after $MAX_RETRIES attempts"
exit 1
