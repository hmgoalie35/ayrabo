#!/usr/bin/env bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

was_changed_in_last_commit () {
    git diff-tree --name-only -r HEAD HEAD~ | grep -e "^$1$"
}

# For reference

#if [[ $(was_changed_in_last_commit "dev_fixtures.json") ]]; then
#    print_step "Applying fixtures"
#    python manage.py loaddata dev_fixtures
#fi

print_step "Installing npm packages"
npm install

print_step "Installing pip packages"
source venv/bin/activate
pip install -r requirements.txt

print_step "Running migrations"
python manage.py migrate

# TODO Change this to development seeding, loaddata wipes all local data...
#print_step "Applying fixtures"
#python manage.py loaddata dev_fixtures

print_step "Done"
