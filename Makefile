.PHONY: lint format test coverage fix

RUN = poetry run

lint:
	$(RUN) ruff check

format:
	$(RUN) ruff format --diff

test:
	$(RUN) python -m unittest

coverage:
	$(RUN) coverage run -m unittest
	$(RUN) coverage report -m
	$(RUN) coverage html

fix:
	$(RUN) ruff format
	$(RUN) ruff check --fix
