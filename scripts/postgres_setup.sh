#!/bin/sh

psql --command "CREATE DATABASE sasmodeldatabase;"
psql --command "CREATE USER sasmodeluser;"
psql --command "GRANT ALL PRIVILEGES ON DATABASE sasmodeldatabase TO sasmodeluser;"