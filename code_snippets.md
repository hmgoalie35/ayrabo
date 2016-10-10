# Useful code snippets

### Testing Related

* `coverage run manage.py test && coverage html`
    * Determines coverage for unit and functional tests

### Misc.
* You can change the string displayed by an object in modelChoice & modelMultipleChoice select menus to any string you want (defaults to `__str__`) with the `label_from_instance` method

* Update pip packages `pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U`

* `./manage.py dumpdata sites account sports leagues divisions teams auth.user userprofiles coaches players referees managers seasons authtoken --indent=4 -o escoresheet/fixtures/dev_fixtures.json`
    * Outputs all data in the db to dev_fixtures.json file
    * Add more apps to the command as new apps are added

* The bootstrap-chosen bower package requires bootstrap's sass because it references bootstrap less variables. My solution is to just compile it myself with sass using the bootstrap-sass repo. Use the following commands
    * Make sure bootstrap-chosen is in the static folder, if it isn't add it to BOWER_INSTALLED_APPS and run `./manage.py bower install`
    * `cd static/bootstrap-chosen/`
    * Run `git clone --depth=1 https://github.com/twbs/bootstrap-sass`
    * Add `@import "bootstrap-sass/assets/stylesheets/_bootstrap.scss";` right above the first import in bootstrap-chosen.scss. This makes all of the bootstrap variables available to the bootstrap-chosen scss.
    * Run `sassc bootstrap-chosen.scss bootstrap-chosen.css` and remove the bootstrap css (which is from lines 1 - 5816)
    * Delete the bootstrap-sass repo
    
    Turns out the chosen-bootstrap bower package (completely different from bootstrap-chosen above) is much better

* `./manage.py reset_db && ./manage.py migrate && ./manage.py loaddata dev_fixtures`
