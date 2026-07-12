.PHONY: install test serve lint release-check clean

install:
	python3 -m pip install -e ".[train]"

test:
	python3 -m pytest tests/ -q

serve:
	astro serve

lint:
	python3 -m py_compile src/astro/*.py tests/*.py

release-check:
	python3 scripts/release_check.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache *.egg-info
