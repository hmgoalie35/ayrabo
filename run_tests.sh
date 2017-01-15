#!/usr/bin/env bash

set -e

print_step () {
    printf "\n\n>>> $1\n\n"
}

COVERAGE_MIN=94

# Need to activate the virtualenv when running tests locally
if [ -e venv ]; then
    source venv/bin/activate
fi

print_step "Running unit/functional tests"
coverage erase
coverage run manage.py test --parallel --failfast
coverage combine && coverage report --fail-under=${COVERAGE_MIN}


# Doesn't really make sense to run coverage for behave. Those tests are just meant to check basic usability
print_step "Running integration tests"
python manage.py behave
