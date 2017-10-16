# Useful code snippets

### Testing Related

* `coverage run manage.py test --parallel && coverage combine && coverage html`
    * Determines coverage for unit and functional tests

### Misc.
* You can change the string displayed by an object in modelChoice & modelMultipleChoice select menus to any string you want (defaults to `__str__`) with the `label_from_instance` method

* Update pip packages `pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U`

* `./manage.py dumpdata sites account sports leagues divisions teams auth.user userprofiles coaches players referees managers seasons authtoken --indent=4 -o escoresheet/fixtures/dev_fixtures.json`
    * Outputs all data in the db to dev_fixtures.json file
    * Add more apps to the command as new apps are added

* `./manage.py reset_db && ./manage.py migrate && ./manage.py loaddata dev_fixtures`

### Factory Boy/Faker/Fuzzy
* `from factory import Faker`
    * This is a wrapper around the actual faker library
    * Use as follows: `name = Faker('last_name_male')`, the arg to the constructor is the name of a provider. https://faker.readthedocs.io/en/master/providers.html
* To use the faker library standalone (generate fixture data, etc.)
    * `from faker import Faker`, `fake = Faker()`, `faker.last_name_male()`
* The fuzzy module from factory-boy doesn't seem to be deprecated as of yet (10/10/17).
    * Can still use it, but really no need. The faker library has almost the same functionality. The only thing missing is specifying a suffix on randomly generated text. (Division)
    * Can always fall back to using factory boy's lazy functions if need be.
