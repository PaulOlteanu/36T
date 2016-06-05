.PHONY: docs test

help:
	@echo "  env         create a development environment using virtualenv"
	@echo "  deps        install dependencies using pip"
	@echo "  clean       remove unwanted files like .pyc's"
	@echo "  lint        check style with flake8"
	@echo "  test        run all your tests using py.test"

env:
	python -m venv venv && make deps

deps:
	./venv/bin/pip install -r requirements.txt

clean:
	./venv/bin/python manage.py clean

lint:
	flake8 --exclude=env .

test:
	./venv/bin/py.test tests
