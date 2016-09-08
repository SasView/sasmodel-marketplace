eval "$(ssh-agent -s)"
chmod 600 .travis/deploy_key.pem
ssh-add .travis/deploy_key.pem
git remote add deploy www-data@danse.chem.utk.edu:/var/www/marketplace.sasview.org
git push deploy
