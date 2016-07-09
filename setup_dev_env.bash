#!/bin/bash

if [ `uname` != "Linux" ]; then
    echo "This install script is only meant for linux"
    exit 0
fi

echo "Updating/upgrading apt packages"
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove -y

echo "Fetching nodejs"
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -

echo "Installing apt packages"
sudo apt-get install python3-pip python-pip nodejs -y

echo "Installing npm packages"
sudo npm -g install phantomjs-prebuilt bower yuglify

echo "Installing global pip packages"
sudo pip install virtualenvwrapper

echo "Adding env vars for virtualenvwrapper"
if [ $SHELL == "/bin/bash" ] ; then
    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
    echo "export PROJECT_HOME=$HOME/Development" >> ~/.bashrc
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
    source ~/.bashrc
elif [ $SHELL == "/bin/zsh" ] ; then
    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.zshrc
    echo "export PROJECT_HOME=$HOME/Development" >> ~/.zshrc
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.zshrc
    source ~/.zshrc
fi

echo "Creating virtualenv"
mkvirtualenv escoresheet -p `which python3`

echo "Installing project pip packages"
pip install -r requirements.txt

echo "Symlinking local_settings file"
cd escoresheet/settings/ && ln -s local_settings.py.dev local_settings.py ; cd ../../

echo "Running initial migrations and loading test data"
python manage.py migrate
python manage.py loaddata dev_only

echo "Running tests..."

python manage.py test apps/

if [ $? -ne 0 ] ; then
    echo "Error running unit/functional tests"
fi

python manage.py behave features/

if [ $? -ne 0 ] ; then
    echo "Error running integration tests"
fi

echo "Done"
