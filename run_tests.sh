#!/usr/bin/env bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

# Need to activate the virtualenv when running tests locally
if [ -e venv ]; then
    source venv/bin/activate
else
    echo "Failed to activate virtualenv"
    exit 1
fi

# TODO run with coverage (parallel mode)
print_step "Running unit/functional tests"
./manage.py test --parallel --failfast

print_step "Running integration tests"
./manage.py behave
