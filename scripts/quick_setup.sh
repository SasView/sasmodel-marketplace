#!/bin/sh

# Get some path names first, to be a bit more robust!
SCRIPTPATH=$(readlink -f "$0")
SCRIPTDIRECTORY=$(dirname "$SCRIPTPATH")
MARKETDIRECTORY=$(dirname "$SCRIPTDIRECTORY")
TARGETDIRECTORYPATH="/var/www/marketplace.sasview.org"

# First let's move the directory into place and then move there
sudo mkdir /var/www
sudo mv "$MARKETDIRECTORY" "$TARGETDIRECTORYPATH"
cd "$TARGETDIRECTORYPATH"

# Install all the relevant software via apt
sudo apt install -y apache2
sudo apt install -y apache2-dev
sudo apt install -y mysql
sudo apt install -y python3-dev
sudo apt install -y python3-setuptools
sudo apt install -y libpq-dev

# Setup Python and get pip installed
sudo ln -s /usr/bin/python3 /usr/bin/python
sudo python /usr/lib/python3/dist-packages/easy_install.py pip

# Clone the git repo and install the required Python packages for the marketplace
sudo -H pip install -r "$TARGETDIRECTORYPATH/requirements.txt"

# Set up MySQL
echo "mysql:mysql" | sudo chpasswd
sudo su - mysql -c "$TARGETDIRECTORYPATH/scripts/mysql_setup.sh"

# Initialise the marketplace
sudo cp "$TARGETDIRECTORYPATH/sasmarket/settings.py.quicksetup.example" "$TARGETDIRECTORYPATH/sasmarket/settings.py"
sudo python "$TARGETDIRECTORYPATH/manage.py" migrate

# Prepare Apache
sudo cp "$TARGETDIRECTORYPATH/sasmarket/marketplace.sasview.org.conf.example" "/etc/apache2/sites-enabled/marketplace.sasview.org.conf"
mod_wsgi-express module-config | sudo tee /etc/apache2/mods-enabled/wsgi_mod.load

git clone https://github.com/SasView/sasmodels
sudo "$TARGETDIRECTORYPATH/scripts/update_sasmodels.sh"

# Restart the Apache web service
sudo rm /etc/apache2/sites-enabled/000-default.conf
sudo service apache2 restart
