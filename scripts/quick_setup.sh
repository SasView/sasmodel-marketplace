#!/bin/sh

# Get some path names first, to be a bit more robust!
SCRIPTPATH=$(readlink -f "$0")
SCRIPTDIRECTORY=$(dirname "$SCRIPTPATH")
MARKETDIRECTORY=$(dirname "$SCRIPTDIRECTORY")
TARGETDIRECTORYPATH="/var/www/marketplace.sasview.org"

# First let's move the directory into place and then move there
mv "$MARKETDIRECTORY" "$TARGETDIRECTORYPATH"
cd "$TARGETDIRECTORYPATH"

# Install all the relevant software via apt
sudo apt install apache2
sudo apt install apache2-dev
sudo apt install postgresql
sudo apt install python3-dev
sudo apt install python3-setuptools

# Setup Python and get pip installed
sudo ln -s /usr/bin/python3 /usr/bin/python 
sudo python /usr/lib/python3/dist-packages/easy_install.py pip

# Clone the git repo and install the required Python packages for the marketplace
sudo pip install -r requirements.txt

# Set up Postgres
echo "postgres:postgres" | sudo chpasswd
chmod 755 scripts/postgres_setup.sh
sudo su - postgres -c scripts/postgres_setup.sh

# Initialise the marketplace
sudo cp sasmarket/settings.py.example sasmarket/settings.py
sudo python manage.py migrate

# Prepare Apache
sudo cp sasmarket/marketplace.sasview.org.conf.template /etc/apache2/sites-enabled/marketplace.sasview.org.conf
chmod 755 scripts/mod_wsgi_generator.sh
./scripts/mod_wsgi_generator.sh

# Restart the Apache web service
sudo service apache2 restart