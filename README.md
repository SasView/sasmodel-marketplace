# SasMarket    
A marketplace website for sharing custom model files for [SasView](https://github.com/SasView/sasview)    
[![Build Status](https://travis-ci.org/SasView/sasmodel-marketplace.svg?branch=master)](https://travis-ci.org/SasView/sasmodel-marketplace)  

Deployed at http://marketplace.sasview.org

## Deployment notes
* settings.py on the deployment server is different from the one in Github  
  * Secret keys and passwords are in there!  
* Deployment is semi-automatic:
  * When changes are pushed to Github, a Travis job is kicked off to test.
  * If the tests pass, the code is pushed to a git repo on the deployment server.
  * If any new static files are added, run the following on the server:
    * ```cd /var/www/marketplace.sasview.org```  
    * ```source virtualenv/bin/activate``` which should give a prompt beginning
     with ```(virtualenv)```
    * Collect static files with ```sudo python manage.py collectstatic```
* Any changes made won't take effect until Apache is reloaded with ```sudo service apache2 reload```

## Developer notes    
*   Ensure you have a Postgresql server up and running  
*   Run `pip install -r requirements.txt`  
*   Rename `sasmarket/settings.py.example` to `sasmarket/settings.py` and
fill in the database details.     
*   Run `python manage.py runserver`  
