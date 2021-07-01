#!/bin/sh

mysql -e "CREATE DATABASE marketplace;"
mysql -e "CREATE USER mysql WITH PASSWORD 'test';"
mysql -e "GRANT ALL PRIVILEGES ON DATABASE marketplace TO mysql;"