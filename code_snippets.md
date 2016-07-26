# Useful code snippets

### Testing Related

* `coverage run manage.py test apps/ && coverage html`
    * Determines coverage for unit and functional tests

### Misc.
* You can change the string displayed by an object in modelChoice & modelMultipleChoice select menus to any string you want (defaults to `__str__`) with the `label_from_instance` method

* Update pip packages `pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U`
