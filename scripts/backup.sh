#!/bin/bash

#RUN THIS SCRIPT AS ROOT

# Do the backup!

BASE_WEB_DIR="/var/www/marketplace.sasview.org"
TODAYS_DATE="$(date +%Y-%m-%d)"
HOME=$BASE_WEB_DIR
zip -9 -r --exclude=*.dropbox* --exclude=*Dropbox* $BASE_WEB_DIR/Dropbox/$TODAYS_DATE_sasmarket_backup.zip $BASE_WEB_DIR