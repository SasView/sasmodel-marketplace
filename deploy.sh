eval "$(ssh-agent -s)"
chmod 600 .travis/deploy_key.pem
ssh-add .travis/deploy_key.pem
git remote add deploy danse.chem.utk:/var/www/marketplace.sasview.org
git push deploy
