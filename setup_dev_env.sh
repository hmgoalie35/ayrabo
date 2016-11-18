#!/usr/bin/env bash

if [ $(uname) != "Linux" ]; then
    echo "This install script is only meant for linux"
    exit 0
fi


print_step () {
    printf "\n\n>>> $1\n\n"
}

print_step "Updating/upgrading apt packages"
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove -y

print_step "Fetching nodejs"
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -

print_step "Installing apt packages"
sudo apt-get install python3-pip python-pip nodejs -y

print_step "Installing npm packages"
npm install

print_step "Installing global pip packages"
sudo pip install virtualenvwrapper

print_step "Configuring virtualenvwrapper"
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
else
    echo "The shell you are using needs to be added to the if elif else chain in this file"
    exit 1
fi

print_step "Creating virtualenv"
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv escoresheet -p `which python3`
workon escoresheet

print_step "Installing project pip packages"
pip install -r requirements.txt

print_step "Installing pre-commit"
pre-commit install

print_step "Symlinking local_settings file"
cd escoresheet/settings/ && ln -s local_settings.py.dev local_settings.py ; cd ../../

if grep -q django.db.backends.sqlite3 escoresheet/settings/local_settings.py ; then
    print_step "Detected local sqlite3 database, running initial migrations and loading test data"
    python manage.py migrate
    python manage.py loaddata dev_fixtures
fi

print_step "Running tests..."

bash run_tests.sh

print_step "Done"
