#!/bin/bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

if [ "$1" == "--hard" ]; then
    print_step "Removing node_modules/ and venv/ folders"
    rm -rf node_modules/
    deactivate || true
    rm -rf venv/
fi

if [ ! -e venv ]; then
    print_step "Creating python virtual env"
    python3.6 -m venv venv/
fi

print_step "Installing python packages"
source venv/bin/activate && pip install -U pip && pip install -U -r requirements.txt

print_step "Installing node and npm"
source ~/.nvm/nvm.sh && nvm install && nvm install-latest-npm

print_step "Installing node packages"
npm install

print_step "Starting postgres docker container"
docker-compose build --pull --parallel && docker-compose up -d

print_step "Waiting for postgres docker container to start"
sleep 4

print_step "Running migrations"
source venv/bin/activate && python manage.py migrate

print_step "Seeding initial data"
source venv/bin/activate && python manage.py seed

printf "\nMake sure to run the webpack watcher to compile your static assets: 'npm run dev'\n"
print_step "Done"
