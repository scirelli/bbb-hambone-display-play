SHELL:=/usr/bin/env bash

VENV_DIR=.venv
VENV_BIN=$(VENV_DIR)/bin

PIP=$(VENV_BIN)/pip
PYTHON=$(VENV_BIN)/python

.PHONY: all
all: test

$(VENV_DIR):
	@echo 'Createing a virtual environment'
	@python3 -m venv --prompt $(notdir $(CURDIR)) ./$(VENV_DIR)
	@echo 'Environment created. Run "source ./$(VENV_DIR)/bin/activate" to activate the virtual environment.\n"deactivate" to exit it.'

.update-pip: ## Update pip
	@$(PIP) install -U 'pip'

.install-deps-dev: $(VENV_DIR)
	@$(PIP) install --require-virtualenv --requirement requirements-dev.txt
	@touch .install-deps-dev

.develop: .install-deps-dev
	@$(PIP) install --require-virtualenv --editable .
	@touch .develop

.PHONY: install-prod
install-prod:  ## Install non-dev environment
	@pip install --target . --requirement requirements.txt

.PHONY: install-dev
install-dev: .develop ## Install development environment

.git/hooks/pre-commit: .develop
	@$(VENV_BIN)/pre-commit install && \
	$(VENV_BIN)/pre-commit autoupdate

install-pre-commit: .git/hooks/pre-commit ## Install Git pre-commit hooks to run linter and mypy


.PHONY: fmt format
fmt format: ## Format code
	@$(PYTHON) -m pre_commit run --all-files --show-diff-on-failure

.PHONY: mypy
mypy:  ## Static type checking
	@$(VENV_BIN)/mypy

.PHONY: lint
lint: fmt mypy  ## Lint source code

.PHONY: test
test: .develop  ## Run unit tests
	@$(VENV_BIN)/pytest -q

.PHONY: vtest
vtest: .develop ## Verbose tests
	@$(VENV_BIN)/pytest -v

.PHONY: vvtest
vvtest: .develop ## More verbose tests
	@$(VENV_BIN)/pytest -vv

.PHONY: dbtest
dbtest: .develop ## Debuggable tests
	@$(VENV_BIN)/pytest --capture=no -vv

.PHONY: viewCoverage
viewCoverage: htmlcov ## View the last coverage run
	open -a "Google Chrome" htmlcov/index.html

.PHONY: shell
shell: $(VENV_DIR) ## Open a virtual environment
	@echo 'Activating virtual environment.' && $(SHELL) --init-file <(echo ". ~/.bashrc; . $(VENV_BIN)/activate;")

.PHONY: clean
clean: ## Remove all generated files and folders
	@$(VENV_BIN)/pre-commit uninstall || true
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
	@rm -f .install-deps-dev
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
