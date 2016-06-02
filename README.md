# escoresheet
Sport scoresheets for the digital age

# Dependencies

* python3
* pip3
* virtualenv and/or virtualenvwrapper (virtualenvwrapper recommended)
* node.js
    * bower
    * phantomjs-prebuilt (prod only)
    * yuglify (prod only)
* apt-get packages
    * python3-pip
    * python3-dev

*nix system recommended, Linux VM will also suffice

# Installation

1. Clone the repo and cd in it
2. ```mkvirtualenv env -p `which python3` ```
    * Swap `mkvirtualenv` with `virtualenv` if you use virtualenv
    * You can replace env with the name of the virtualenv you want to create
3. Make sure your virtual environment is activated, then run `pip install -r requirements.txt`
4. Install node.js
5. `[sudo] npm -g install bower`
    * yuglify and phantomjs-prebuilt are only for prod 
    * You might need to run as root
6. `cd escoresheet/settings/ && ln -s local_settings.py.dev local_settings.py`

# Integration Tests

### Writing Integration Tests
  * TODO

### Running Integration Tests (via selenium, phantomjs)
1. Make sure you are in the directory where manage.py is
2. Run `python manage.py behave`
    * You can specify specific files or directories to test i.e. `python manage.py behave features/account/Login.feature`

# Functional and Unit Tests

### Writing Functional and Unit Tests
  * TODO

### Running Functional and Unit Tests
1. Make sure you are in the directory where manage.py is
2. Run `python manage.py test apps/`
    * **Note:** You need to specify the apps/ folder
