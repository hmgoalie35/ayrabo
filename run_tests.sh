#!/usr/bin/env bash

set -e

print_step () {
    printf "\n\n>>> $1\n\n"
}

COVERAGE_MIN=94
# Default to running all tests
TESTS='all'
if [ ! -z $1 ]; then
    TESTS=$1
fi

# Need to activate the virtualenv when running tests locally
if [ -e venv ]; then
    source venv/bin/activate
fi

if [ ${TESTS} == 'all' ] || [ ${TESTS} == 'unit' ]; then
    print_step "Running unit/integration tests"
    coverage erase
    coverage run manage.py test --parallel --failfast
    coverage combine && coverage report --fail-under=${COVERAGE_MIN}
fi

if [ ${TESTS} == 'all' ] || [ ${TESTS} == 'accept' ]; then
    # Doesn't really make sense to run coverage for behave. Those tests are just meant to check basic usability
    print_step "Running acceptance tests"
    python manage.py behave
fi
