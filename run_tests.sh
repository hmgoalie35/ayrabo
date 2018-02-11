#!/usr/bin/env bash

set -e

print_step () {
    printf "\n\n>>> $1\n\n"
}

print_status () {
    # $2 is the color value from https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
    # $3 is the unicode value
    echo -e "\033[0;$2m$1 \u$3\033[0m\n"
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

print_step "Running flake8"
flake8
if [ "$?" == "0" ]; then
    print_status "Success" "32" "2713"
else
    print_status "Failed" "31" "2717"
    exit 1
fi

if [ ${TESTS} == 'all' ] || [ ${TESTS} == 'unit' ]; then
    print_step "Running unit/integration tests"
    coverage erase
    coverage run manage.py test --parallel --failfast
    coverage combine && coverage report --fail-under=${COVERAGE_MIN}
fi

if [ ${TESTS} == 'all' ] || [ ${TESTS} == 'jest' ]; then
    print_step "Running jest tests"
    npm run test-ci
fi

if [ ${TESTS} == 'all' ] || [ ${TESTS} == 'accept' ]; then

    if [ ! -d "static/dist" ]; then
        printf "\n\nYou need to run 'npm run dev' or 'npm run build' before running acceptance tests"
        exit 1
    fi

    # Doesn't really make sense to run coverage for behave. Those tests are just meant to check basic usability
    print_step "Running acceptance tests"
    python manage.py behave
fi
