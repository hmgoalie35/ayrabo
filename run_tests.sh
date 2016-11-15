#!/usr/bin/env bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

# Need to activate the virtualenv when running tests locally
if [ -e ~/.virtualenvs/escoresheet/bin/activate ]; then
    source ~/.virtualenvs/escoresheet/bin/activate
fi

# TODO run with coverage (parallel mode)
print_step "Running unit/functional tests"
./manage.py test --parallel --failfast

print_step "Running integration tests"
./manage.py behave
