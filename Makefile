.PHONY: test clean update lint coverage

ENV=

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf build
	rm -rf dist
	python3 setup.py clean

update:
	${ENV}pip install -U -r test/requirements.txt

lint:
	${ENV}flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	${ENV}flake8 . --count --statistics

coverage:
	${ENV}pytest --cov-report term --cov-report xml --cov=scrapy_count_filter test/

test:
	${ENV}pytest -ra -sv test/
