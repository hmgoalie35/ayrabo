# escoresheet
Sport scoresheets for the digital age

Dev: [![Build Status](https://travis-ci.org/hmgoalie35/escoresheet.svg?branch=dev)](https://travis-ci.org/hmgoalie35/escoresheet)

Prod: [![Build Status](https://travis-ci.org/hmgoalie35/escoresheet.svg?branch=master)](https://travis-ci.org/hmgoalie35/escoresheet)

# About
This is a personal/entrepreneurial project I had the idea for in college and started working on after graduating in May 2016. Having played club ice hockey for 4 years, I was always shocked at how painful it was to report game scores to the league. Team managers would have to call and tell the league the score of the game, and then manually enter in goals, assists, penalties, etc. on a website. I thought it would be a great idea to simply cut out all of this unneeded work. Cue escoresheet (name is a WIP). The goal is to provide a web based scoresheet that can facilitate keeping score for scorekeepers and keep everybody updated with the progress of the game. Every goal, assist, penalty, etc. for a given game is automatically synced to our servers, which allows us to live update our site to keep the game stats up to date. I aim to make this compatible with any sport, not just ice hockey. Users can even register as players/coaches/managers/referees for multiple sports and all of their stats will be available in one centralized location.

One potential problem is internet access in/on arenas, fields, etc. In this day and age it is becoming easier and easier to put up a wifi hotspot in the most unexpected places. My solution to this is an offline application that can by synced with our servers when the game is finished. Simply connect the device to the internet and voila. 

Right now the MVP I am aiming for is completely web browser based, and a computer or large tablet (really something with a large enough screen) with internet access is required. Future releases will potentially include a mac/windows/linux desktop application (Qt or Electron?) that can work with or without internet access and will tap into an API. This project will eventually be moved to a pure SOA so the front (Angular2?) and back ends can be completely separate.

A license has been intentionally excluded. See http://choosealicense.com/no-license/ for more information.

# Apt Dependencies

* python3-pip
* python-pip
* nodejs

# Pip Packages (to be installed globally)
* virtualenv or virtualenvwrapper (virtualenvwrapper recommended)

# Npm Packages (to be installed locally)
* bower
* phantomjs-prebuilt
* yuglify (prod only)

*nix system recommended, Linux VM will also suffice

# Installation

You can either follow the instructions below or run setup_dev_env.sh (which installs necessary packages and runs the commands below)

*This project uses pre-commit, whenever you commit files a few optimizers, code checkers, etc. will be run to check the committed files for any errors/potential bugs*

1. Clone the repo and cd into it
2. Make sure the dependencies above are installed
3. Run `npm install`
4. ```mkvirtualenv escoresheet -p `which python3` ```
    * Swap `mkvirtualenv` with `virtualenv` if you use virtualenv
    * You can replace escoresheet with the name of the virtualenv you want to create
5. Make sure your virtual environment is activated, then run `pip install -r requirements.txt`
6. Run `pre-commit install` to install pre-commit.
7. `sudo npm -g install phantomjs-prebuilt bower yuglify`
    * yuglify is only for prod but for consistency install it anyway
    * You will likely need to run as root
8. `cd escoresheet/settings/ && ln -s local_settings.py.dev local_settings.py ; cd ../../`
    * This allows development settings to override production settings.

Only do the following if you are using your own local sqlite database or if the database is brand new

1. Apply migrations with `python manage.py migrate`
2. Load useful development related data with `python manage.py loaddata dev_fixtures`
    * dev_fixtures is a json fixture file located in escoresheet/fixtures/


Lastly, run unit/functional/integration tests to make sure everything is setup correctly (see below)


* `bash run_tests.sh` will run all tests

NOTE: The tests may take a few minutes

# Integration Tests

### Writing Integration Tests
  * See [Writing Integration Tests](https://github.com/hmgoalie35/escoresheet/wiki/Writing-Integration-Tests)

### Running Integration Tests (via selenium, phantomjs)
1. Make sure you are in the directory where manage.py is
2. Run `python manage.py behave`
    * You can specify specific files to test via regex i.e. `python manage.py behave --include <regex>`

# Functional and Unit Tests

### Writing Functional and Unit Tests
  * See [Writing Unit & Functional Tests](https://github.com/hmgoalie35/escoresheet/wiki/Writing-Unit-&-Functional-Tests)

### Running Functional and Unit Tests
1. Make sure you are in the directory where manage.py is
2. Run `python manage.py test`
    * You can specify specific test files or test classes for an app i.e. `python manage.py test userprofiles.tests.test_models.UserProfileModelTests`

# Running tests with coverage
* `coverage run manage.py test && coverage html`
* `coverage run manage.py behave && coverage html`
