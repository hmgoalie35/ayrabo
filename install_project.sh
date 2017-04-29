#!/usr/bin/env bash

if [ $(uname) != "Linux" ]; then
    echo "This install script is only meant for linux"
    exit 0
fi


print_step () {
    printf "\n\n>>> $1\n\n"
}

print_step "Installing npm packages"
npm install

print_step "Installing virtualenv"
sudo pip3 install virtualenv

print_step "Creating virtualenv with python3 interpreter"
virtualenv venv -p $(which python3)
source venv/bin/activate

print_step "Installing python packages"
pip install -r requirements.txt

print_step "Installing pre-commit"
pre-commit install

print_step "Symlinking local_settings file"
cd escoresheet/settings/ && ln -s local_settings.py.dev local_settings.py ; cd ../../

print_step "Starting postgres docker container"
cd devops/docker && docker-compose up -d && cd ../../
sleep 8

print_step "Running migrations"
python manage.py migrate

print_step "Loading test data"
if [ -d /var/lib/ess ]; then
    echo "Found existing database, skipping fixture loading"
    echo "You can delete existing postgres db files by running `sudo rm -r /var/lib/ess`"
else
    python manage.py loaddata dev_fixtures
fi

print_step "Running tests..."

bash run_tests.sh

print_step "Done"
