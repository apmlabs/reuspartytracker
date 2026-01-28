#!/bin/bash
# Daily InfluxDB backup for Reus Party Tracker

BACKUP_DIR="/home/ubuntu/mcpprojects/reuspartytracker/backups"
TOKEN="gOMGaI8MvS6jUV0J7XnbWhwG1KER0mURd-VoyY7KIrCUhkTGeEr_3r2fBUtp9ugvzrcrO8UuZkLF6KmLe_3tEA=="
BUCKET="party_data"
ORG="reusparty"
DATE=$(date +%Y-%m-%d)

# Create backup
influx backup "$BACKUP_DIR/$DATE" --token "$TOKEN" --org "$ORG" --bucket "$BUCKET" 2>&1

# Keep only last 7 days
find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $DATE"
