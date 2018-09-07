# SasMarket    
A marketplace website for sharing custom model files for [SasView](https://github.com/SasView/sasview)  

[![Build Status](https://travis-ci.org/SasView/sasmodel-marketplace.svg?branch=master)](https://travis-ci.org/SasView/sasmodel-marketplace)

Deployed at http://marketplace.sasview.org

## Quick setup instructions (Ubuntu)

A script has been generated that will execute all the steps shown in the next section to provide an automated way of going from a fresh Ubuntu install to having a running marketplace, to run this you will need to type the following into an Ubuntu console

```
git clone https://github.com/SasView/sasmodel-marketplace
cd sasmodel-marketplace/scripts
chmod 755 quick_setup.sh
./quick_setup.sh
```
You should now be able to access the newly created SasView Marketplace site by navigating to 127.0.0.1 on a web browser the server itself or by navigating to the server's external IP address in a web browser on another machine.

**N.B.** This setup is only recommended for testing and development as the passwords generated as the same as the usernames and therefore are highly insecure and **not** suitable for deployment.


## Full setup instructions (Ubuntu)
These instructions will create an installation of the SasView marketplace using the system Python installation on Ubuntu. This setup is suitable for environments where there is only one web service present on the server or virtual machine. Should the intention be to serve multiple sites from one machine the use of virtual Python environments is **strongly** recommended. More information about setting up and using a virtual environment can be [found on these pages](http://www.google.com). These instructions should be usable for other Linux flavours, however, modifications may be required to the steps delineated below.  

* First download and install Ubuntu server edition, which is currently [Ubuntu 18.04.1 LTS](https://www.ubuntu.com/download/server/thank-you?version=18.04.1&architecture=amd64)  

* After installation the ```apache2```, ```apache2-dev```, ```postgresql```, ```python3-dev``` and ```python3-setuptools``` packages will need to be installed *via* the system package manager, for Ubuntu this is ```apt``` and should be invoked thusly

  ```
  sudo apt install *package-name*
  ```

* As, by default, the command ```python``` is undefined with only ```python3``` is installed we will make a symbolic link to allow both users and software to use Python 'as normal' by invoking

  ```
  sudo ln -s /usr/bin/python3 /usr/bin/python 
  ```

* With Python setup it is then necessary to use ```easy_install``` to install ```pip``` via

  ```
  sudo python /usr/lib/python3/dist-packages/easy_install.py pip
  ```

* With all the required operating system packages installed it is then necessary to clone the git repository into the appropriate location for the Apache web server by entering

  ```
  sudo git clone https://github.com/SasView/sasmodel-marketplace /var/www/marketplace.sasview.org
  ```

* With the repository downloaded and ```pip``` installed it is then possible to install all the marketplace dependencies using the following

  ```
  sudo pip install -r /var/www/marketplace.sasview.org/requirements.txt
  ```

* Now, with all the appropriate software loaded, it is subsequently possible to set up the database in which all the models will be saved. Assuming that this is a new installation of Ubuntu this will also require setting up the ```postgres``` user with a password using

  ```
  sudo passwd postgres
  ```

  * **N.B.** in these setup instructions all passwords will be the same as the entity that requires the password, *i.e.* the ```postgres``` user will have the password ```postgres```. **This is not a suitable paradigm for deployment systems.**

* You can now ```su``` to this user in order to use the ```psql``` command

  ``` 
  su postgres
  ***insert super-secret password***
  psql
  ```

* From ```psql``` you can then set up a postgres user and a storage database by entering in the following three commands

  ```
  CREATE DATABASE sasmodeldatabase;
  CREATE USER sasmodeluser WITH PASSWORD 'sasmodeluser';
  GRANT ALL PRIVILEGES ON DATABASE sasmodeldatabase TO sasmodeluser;
  ```

* With the database created you may ```\q``` from ```psql``` and ```exit``` from the ```postgres``` user shell, returning to the ```/var/www/marketplace.sasview.org``` directory for the subsequent steps

* It is now necessary to alter the ```settings.py``` file for the site in the ```sasmarket``` directory. Taking a copy of the example file is recommended  

  ```
  sudo cp /var/www/sasmarket/settings.py.example /var/www/sasmarket/settings.py
  ```  

  Inside this file the following will need to be altered

  * Line 26 - Debug boolean (when ready for deployment) ```DEBUG = False```
  * Line 28 - Allowed hosts, *i.e.* ```ALLOWED_HOSTS = ['127.0.0.1']```
  * Line 82 - Database name ``` 'NAME': 'sasmodeldatabase' ```
  * Line 83 - Database user ``` 'USER': 'sasmodeluser' ```
  * Line 84 - Database password ``` 'PASSWORD': 'sasmodeluser' ```

* Following the installation of the marketplace dependencies it is necessary to perform a migration, from the root marketplace directory, using

  ```
  sudo python manage.py migrate
  ```

* Now that the site is configured, we must configure Apache accordingly, first copy the example Apache configuration file into the ```sites-enabled``` folder

  ``` 
  sudo cp /var/www/sasmarket/marketplace.sasview.org.conf.example /etc/apache2/sites-enabled/marketplace.sasview.org.conf
  ```

* Subsequently the ```wsgi``` modification must be made available to Apache for which a script exists inside the marketplace repository, it can be run by executing

  ```
  /var/www/marketplace.sasview.org/scripts/mod_wsgi_generator.sh
  ```

* The final step is to restart the Apache webserver service by executing

  ```
  sudo service apache2 restart
  ```

  After which the marketplace should be running and accessible from either the server itself *via* 127.0.0.1 or from external hosts using the server's external IP address.


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
