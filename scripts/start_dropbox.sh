#!/bin/bash

BASE_WEB_DIR="/var/www/marketplace.sasview.org"
HOME=$BASE_WEB_DIR

sudo killall dropboxd
cd $BASE_WEB_DIR

sudo wget -O - "https://www.dropbox.com/download?plat=lnx.x86_64" | tar xzf -
sudo nohup $BASE_WEB_DIR/.dropbox-dist/dropboxd > /dev/null