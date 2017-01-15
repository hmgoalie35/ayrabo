#!/usr/bin/env bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

was_changed_in_last_commit () {
    git diff-tree --name-only -r HEAD HEAD~ | grep -e "^$1$"
}

if [[ $(was_changed_in_last_commit "package.json") ]]; then
    print_step "Rebuilding npm packages"
    rm -rf node_modules
    npm install
else
    print_step "No new npm packages"
fi

if [[ $(was_changed_in_last_commit "requirements.txt") ]]; then
    print_step "Rebuilding virtualenv"
    rm -rf venv
    virtualenv venv -p $(which python3)
    source venv/bin/activate
    pip install -r requirements.txt
else
    print_step "No new pypi packages"
fi

print_step "Running migrations"
python manage.py migrate


if [[ $(was_changed_in_last_commit "dev_fixtures.json") ]]; then
    print_step "Applying fixtures"
    python manage.py loaddata dev_fixtures
fi

print_step "Done"
