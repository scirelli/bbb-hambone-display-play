SHELL:=/usr/bin/env bash

.PHONY: all
all: test

.update-pip: ## Update pip
	@pip install -U 'pip'

.install-deps:
	@pipenv install --dev --skip-lock
	@touch .install-deps

.develop: .install-deps
	pipenv install --skip-lock --editable .
	@touch .develop

.PHONY: fmt format
fmt format: ## Format code
	pipenv run python3 -m pre_commit run --all-files --show-diff-on-failure

.PHONY: mypy
mypy:  ## Static type checking
	pipenv run mypy

.PHONY: lint ## Lint source code
lint: fmt mypy

.PHONY: test ## Run unit tests
test: .develop
	@pipenv run pytest -q

.PHONY: vtest
vtest: .develop ## Verbose tests
	@pipenv run pytest -s -v

.PHONY: vvtest
vvtest: .develop ## More verbose tests
	@pipenv run pytest -vv

.PHONY: viewCoverage
viewCoverage: htmlcov ## View the last coverage run
	open -a "Google Chrome" htmlcov/index.html

.PHONY: install
install: .update-pip  ## Install non-dev environment
	@pipenv install --skip-lock

.PHONY: install-dev
install-dev: .develop ## Install development environment

.PHONY: gunicorn
gunicorn:  ## Start gunicorn (would be used in docker)
	@open http://localhost:5000/health
	@pipenv run gunicorn -w 4 -b 127.0.0.1:5000 server:app

.PHONY: run
run-dev:  ## Start gunicorn (would be used in docker)
	@open http://localhost:5000/health
	@env FLASK_APP=src/<project name> \
		 FLASK_ENV=development \
		 FLASK_DEBUG=1 \
		 _CONFIG_FILE=config.py \
		 pipenv run flask run

.git/hooks/pre-commit: .develop
	pipenv run pre-commit install && \
	pipenv run pre-commit autoupdate

install-pre-commit: .git/hooks/pre-commit ## Install Git pre-commit hooks to run linter and mypy

.PHONY: build-docker
build-docker: Dockerfile
	docker build \
		--pull \
		--no-cache \
		--tag "scirelli/bbb-python" \
		--file Dockerfile \
		.

.PHONY: clean
clean: ## Remove all generated files and folders
	@pipenv run pre-commit uninstall || true
	@pipenv --rm || true
	@rm -rf .venv
	@rm -rf `find . -name __pycache__`
	@rm -f `find . -type f -name '*.py[co]' `
	@rm -f .coverage
	@rm -rf htmlcov
	@rm -rf build
	@rm -rf cover
	@rm -f .develop
	@rm -f .flake
	@rm -rf *.egg-info
	@rm -f .install-deps
	@rm -rf .mypy_cache
	@python setup.py clean || true
	@rm -rf .eggs
	@rm -rf .pytest_cache/

.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

.PHONY : help
help :
	@grep -E '^[[:alnum:]_-]+[[:blank:]]?:.*##' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
