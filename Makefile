SHELL := /bin/bash
folder_name =$(shell basename $(shell pwd))

.PHONY: init
init:
	rm -rf ./.venv
	python3 -m venv ./.venv && \
	source .venv/bin/activate

.PHONY: requirements
requirements:
	. .venv/bin/activate && pip install -r requirements.txt

.PHONY: requirements-all
requirements-all: requirements
	. .venv/bin/activate && [ -f ./tests/requirements.txt ] && pip install -r ./tests/requirements.txt

.PHONY: lint
lint:
	. .venv/bin/activate && pip install pylint && pylint --max-line-length=120 --fail-under=8 \
	./backend/*.py \
	./frontend/*.py \
	./frontend/components/*.py \
	./frontend/panels/*.py \
	./*.py

.PHONY: test
test:
	. .venv/bin/activate && coverage run --omit '.venv/*' -m pytest -o junit_suite_name=$(folder_name) --junitxml=./test-results/test-results.xml -v tests/ && coverage report -m

.PHONY: run-cli
run-cli:
	. .venv/bin/activate && python3 entrypoint.py

.PHONY: run-app
run-app:
	. .venv/bin/activate && streamlit run app.py