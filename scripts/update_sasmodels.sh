#!/bin/sh

#RUN THIS SCRIPT AS ROOT

BASE_WEB_DIR="/var/www/marketplace.sasview.org"

# Update the sasmodels repo in the marketplace
cd "$BASE_WEB_DIR/sasmodels"
git pull

cd $"$TARGETDIRECTORYPATH/virtualenv"
source bin/activate
python ../upload_sasmodels.py