.PHONY: help test

help:
	@echo "  env         create a development environment using virtualenv"
	@echo "  deps        install dependencies using pip"
	@echo "  clean       remove unwanted files like .pyc's"
	@echo "  test        run all your tests using py.test"

venv:
	python -m venv venv && make deps

deps:
	./venv/bin/pip install -r requirements.txt

clean:
	./venv/bin/python manage.py clean

test:
	./venv/bin/py.test tests
