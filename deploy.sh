eval "$(ssh-agent -s)"
chmod 600 .travis/travis_rsa
ssh-add .travis/travis_rsa
git remote add deploy git@danse.chem.utk.edu:/home/git/marketplace.sasview.org
git push deploy master
