#!/usr/bin/env bash

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
    virtualenv venv -p `which python3.6`
fi

print_step "Installing pip packages"
source venv/bin/activate
pip install -r requirements.txt

print_step "Installing npm packages"
npm install

print_step "Starting postgres service"

COMPOSE_FILE=devops/docker/docker-compose.yml
docker-compose -f ${COMPOSE_FILE} build --pull && docker-compose -f ${COMPOSE_FILE} up -d

print_step "Running migrations"
python manage.py migrate

# TODO convert old fixtures to seeds.
print_step "Seeding initial data"
python manage.py seed

printf "\nMake sure to run the webpack watcher to compile your static assets: 'npm run dev'\n"
print_step "Done"
