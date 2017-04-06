# SasMarket    
A marketplace website for sharing custom model files for [SasView](https://github.com/SasView/sasview)    
[![Build Status](https://travis-ci.org/SasView/sasmodel-marketplace.svg?branch=master)](https://travis-ci.org/SasView/sasmodel-marketplace)  

Deployed at http://marketplace.sasview.org

## Deployment notes
* settings.py on the deployment server is different from the one in Github  
  * Secret keys and passwords are in there!  
* Deployment is semi-automatic:
  * When changes are pushed to Github, a Travis job is kicked off to test.
  * If the tests pass, the code is pushed to a git repo on the deployment server
  , but this does not deploy the code
  * On the deployment server, do the following:
    * ```cd /var/www/marketplace.sasview.org```  
    * ```git pull```
    * ```source virtualenv/bin/activate``` which should give a prompt beginning
     with ```(virtualenv)```
    * Collect static files with ```sudo python manage.py collectstatic```

## Developer notes    
*   Ensure you have a Postgresql server up and running  
*   Run `pip install -r requirements.txt`  
*   Rename `sasmarket/settings.py.example` to `sasmarket/settings.py` and
fill in the database details.     
*   Run `python manage.py runserver`  
