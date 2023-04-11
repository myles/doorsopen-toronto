.PHONY: all
all: clean setup test lint mypy bandit

.PHONY: setup
setup: pyproject.toml
	poetry install

.PHONY: test
test:
	poetry run pytest --cov=opendata_toronto_doors_open/ --cov-report=xml

.PHONY: lint
lint:
	poetry run black --check .
	poetry run isort --check .
	poetry run ruff check .

.PHONY: lintfix
lintfix:
	poetry run black .
	poetry run isort .
	poetry run ruff . --fix

.PHONY: mypy
mypy:
	poetry run mypy opendata_toronto_doors_open/

.PHONY: bandit
bandit:
	poetry run bandit --recursive --quiet opendata_toronto_doors_open/

.PHONY: clean
clean:
	rm -fr ./.mypy_cache
	rm -fr ./.pytest_cache
	rm -fr ./.ruff_cache
	rm -fr ./dist
	rm -f .coverage
	rm -f coverage.xml
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: build
build:
	poetry run dinesafe-toronto doorsopen-toronto scrape-data doorsopen.db

.PHONY: datasette
datasette: doorsopen.db
	poetry run datasette serve ./doorsopen.db --metadata metadata.json
