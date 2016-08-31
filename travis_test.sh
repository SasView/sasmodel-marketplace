#!/bin/sh
cp sasmarket/settings.py.example sasmarket/settings.py
python manage.py test marketplace
