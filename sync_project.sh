#!/usr/bin/env bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

print_step "Rebuilding npm packages"
rm -rf node_modules
npm install

print_step "Rebuilding virtualenv"
rm -rf venv
virtualenv venv -p $(which python3)
source venv/bin/activate
pip install -r requirements.txt

print_step "Running migrations"
python manage.py migrate

print_step "Applying fixtures"
python manage.py loaddata dev_fixtures
