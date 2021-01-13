#!/bin/bash

#RUN THIS SCRIPT AS ROOT

BASE_WEB_DIR="/var/www/marketplace.sasview.org"

# Update the sasmodels repo in the marketplace
cd "$BASE_WEB_DIR/sasmodels"
git pull

cd "$BASE_WEB_DIR"
python upload_sasmodels.py
