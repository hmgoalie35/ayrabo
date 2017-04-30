# escoresheet
Sport scoresheets for the digital age

Dev: [![Build Status](https://travis-ci.org/hmgoalie35/escoresheet.svg?branch=dev)](https://travis-ci.org/hmgoalie35/escoresheet)

Prod: [![Build Status](https://travis-ci.org/hmgoalie35/escoresheet.svg?branch=master)](https://travis-ci.org/hmgoalie35/escoresheet)

# About
This is a personal/entrepreneurial project I had the idea for in college and started working on after graduating in May 2016. Having played club ice hockey for 4 years, I was always shocked at how painful it was to report game scores to the league. Team managers would have to call and tell the league the score of the game, and then manually enter in goals, assists, penalties, etc. on a website. I thought it would be a great idea to simply cut out all of this unneeded work. Cue escoresheet (name is a WIP). The goal is to provide a web based scoresheet that can facilitate keeping score for scorekeepers and keep everybody updated with the progress of the game. Every goal, assist, penalty, etc. for a given game is automatically synced to our servers, which allows us to live update our site to keep the game stats up to date. I aim to make this compatible with any sport, not just ice hockey. Users can even register as players/coaches/managers/referees for multiple sports and all of their stats will be available in one centralized location.

One potential problem is internet access in/on arenas, fields, etc. In this day and age it is becoming easier and easier to put up a wifi hotspot in the most unexpected places. My solution to this is an offline application that can by synced with our servers when the game is finished. Simply connect the device to the internet and voila. 

Right now the MVP I am aiming for is completely web browser based, and a computer or large tablet (really something with a large enough screen) with internet access is required. Future releases will potentially include a mac/windows/linux desktop application (Qt or Electron?) that can work with or without internet access and will tap into an API. This project will eventually be moved to a pure SOA so the front (Angular2?) and back ends can be completely separate.

A license has been intentionally excluded. See http://choosealicense.com/no-license/ for more information.

*nix system recommended, Linux VM will also suffice

# Installation

See the `install_*.sh` scripts for packages that will be installed, etc.

This project uses pre-commit, whenever you commit files flake8 and some other code quality tools will run to help prevent bugs/errors.

1. Clone the repo and cd into it.
2. Signup for mailtrap https://mailtrap.io/ Emails sent during development will go to mailtrap.
3. Run `cp .env.example .env`. Add in the appropriate values.
4. Run the following:
    * `bash install_dependencies.sh` -- Your system will reboot after this is finished.
    * `bash install_project.sh` -- Run this after system reboot.
    * The last part of the above script runs the test suite, it might take a few minutes

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

# Running the test suite
* Run the `run_tests.sh` file. This will run coverage on unit/functional tests and simply run the integration tests.
