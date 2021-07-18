env:
	virtualenv -p python3 env
pip:
	./env/bin/pip install bumpversion twine
install:
	./env/bin/pip install -e .
all: env pip install

bump:
	./env/bin/bumpversion --current-version 0.1.0 minor setup.py ldtk_intgrid_creator/__init__.py
build:
	./env/bin/python setup.py sdist bdist_wheel
check:
	./env/bin/twine check dist/*
upload-test:
	./env/bin/twine upload --repository-url https://test.pypi.org/legacy/ dist/*
upload:
	./env/bin/twine upload dist/*
