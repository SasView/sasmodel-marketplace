# SasMarket    
A marketplace website for sharing custom model files for [SasView](https://github.com/SasView/sasview)    
[![Build Status](https://travis-ci.org/SasView/sasmodel-marketplace.svg?branch=master)](https://travis-ci.org/SasView/sasmodel-marketplace)  


## Setup    
*   Ensure you have a Postgresql server up and running
*   Run `pip install django psycopg2 django-bootstrap3`
*   Rename `sasmarket/settings.py.example` to `sasmarket/settings.py` and
fill in the database details.    
*   Run `django manage.py runserver`
