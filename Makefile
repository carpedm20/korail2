init:
	pandoc -o README.rst README.md
	cp README.rst ./docs/index.rst
	python setup.py sdist upload

