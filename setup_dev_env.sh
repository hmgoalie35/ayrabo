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

print_step "Installing virtualenv"
sudo pip install virtualenv

print_step "Creating virtualenv with python3 interpreter"
virtualenv venv -p $(which python3)
source venv/bin/activate

print_step "Installing python packages"
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
