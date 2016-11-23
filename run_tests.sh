#!/usr/bin/env bash

print_step () {
    printf "\n\n>>> $1\n\n"
}

# Need to activate the virtualenv when running tests locally
if [ -e venv ]; then
    source venv/bin/activate
fi

print_step "Running unit/functional tests"
coverage run manage.py test --parallel --failfast
coverage combine && coverage report

# TODO Run coverage for behave also?
#coverage erase

print_step "Running integration tests"
python manage.py behave

