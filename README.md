# escoresheet
Sport scoresheets for the digital age

Dev: [![Build Status](https://travis-ci.com/hmgoalie35/escoresheet.svg?token=6sJZQMC4LpsRyFkHBeAL&branch=dev)](https://travis-ci.com/hmgoalie35/escoresheet)

Prod: [![Build Status](https://travis-ci.com/hmgoalie35/escoresheet.svg?token=6sJZQMC4LpsRyFkHBeAL&branch=master)](https://travis-ci.com/hmgoalie35/escoresheet)

# Apt Dependencies

* python3-pip
* python-pip
* nodejs

# Pip Packages (to be installed globally)
* virtualenv or virtualenvwrapper (virtualenvwrapper recommended)

# Npm Packages
* bower
* phantomjs-prebuilt
* yuglify (prod only)

*nix system recommended, Linux VM will also suffice

# Installation

You can either follow the instructions below or run setup_dev_env.bash (which installs necessary packages and runs the commands below)

*This project uses pre-commit, whenever you commit files a few optimizers, code checkers, etc. will be run to check the committed files for any errors/potential bugs*

1. Clone the repo and cd in it
2. Make sure the dependencies above are installed
3. ```mkvirtualenv escoresheet -p `which python3` ```
    * Swap `mkvirtualenv` with `virtualenv` if you use virtualenv
    * You can replace escoresheet with the name of the virtualenv you want to create
4. Make sure your virtual environment is activated, then run `pip install -r requirements.txt`
5. Run `pre-commit install` to install pre-commit.
6. `sudo npm -g install phantomjs-prebuilt bower yuglify`
    * yuglify is only for prod but for consistency install it anyway
    * You will likely need to run as root
7. `cd escoresheet/settings/ && ln -s local_settings.py.dev local_settings.py ; cd ../../`

Only do the following if you are using your own local sqlite database or if the database is brand new

1. Apply migrations with `python manage.py migrate`
2. Load useful development related data with `python manage.py loaddata dev_only`
    * dev_only is a json fixture file located in escoresheet/fixtures/


Lastly, run unit/functional/integration tests to make sure everything is setup correctly (see below)
NOTE: The tests may take a few minutes

# Integration Tests

### Writing Integration Tests
  * TODO

### Running Integration Tests (via selenium, phantomjs)
1. Make sure you are in the directory where manage.py is
2. Run `python manage.py behave features/`
    * You can specify specific files or directories to test i.e. `python manage.py behave features/account/Login.feature`

# Functional and Unit Tests

### Writing Functional and Unit Tests
  * TODO

### Running Functional and Unit Tests
1. Make sure you are in the directory where manage.py is
2. Run `python manage.py test`
    * You can specify specific test files or test classes for an app i.e. `python manage.py test userprofiles.tests.test_models.UserProfileModelTests`
