# DoorsOpen Toronto

A [datasette][datasette] of the City of Toronto's] [DoorsOpen][doorsopen] data.

[datasette]: https://datasette.io/
[doorsopen]: https://www.toronto.ca/explore-enjoy/festivals-events/doors-open-toronto/

## Commands

### Scape DoorsOpen 

The `scrape-data` command will scrape the DoorsOpen JSON data and save it to a 
SQLite database.

```console
foo@bar:~$ poetry run doorsopen-toronto scrape-data dinesafe.db
```

## Develop

You'll need to have [Poetry][poetry], a Python packaging and dependency system,
installed. Once installed you can run:

```console
foo@bar:~$ make setup
```

[poetry]: https://python-poetry.org
