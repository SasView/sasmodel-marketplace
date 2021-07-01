#!/bin/sh

mysql -e "CREATE DATABASE sasmodeldatabase;"
mysql -e "CREATE USER sasmodeluser WITH PASSWORD 'sasmodeluser';"
mysql -e "GRANT ALL PRIVILEGES ON DATABASE sasmodeldatabase TO sasmodeluser;"