#!/bin/bash

#RUN THIS SCRIPT AS ROOT

# Do the backup!

BASE_WEB_DIR="/var/www/marketplace.sasview.org"
TODAYS_DATE="$(date +%Y-%m-%d)"
zip -9 -r --exclude=*.dropbox* --exclude=*Dropbox* Dropbox/$TODAYS_DATE_sasmarket_backup.zip $BASE_WEB_DIR