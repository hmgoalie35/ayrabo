#!/usr/bin/env bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

was_changed_in_last_commit () {
    git diff-tree --name-only -r HEAD | grep "$1"
}

if [[ $(was_changed_in_last_commit "package.json") == 0 ]]; then
    print_step "Rebuilding npm packages"
    rm -rf node_modules
    npm install
fi

if [[ $(was_changed_in_last_commit "requirements.txt") == 0 ]]; then
    print_step "Rebuilding virtualenv"
    rm -rf venv
    virtualenv venv -p $(which python3)
    source venv/bin/activate
    pip install -r requirements.txt
fi

print_step "Running migrations"
python manage.py migrate

print_step "Applying fixtures"
python manage.py loaddata dev_fixtures
