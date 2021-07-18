env:
	virtualenv -p python3 env
pip:
	./env/bin/pip install bumpversion
install:
	./env/bin/pip install -e .
all: env pip install

bump:
	./env/bin/bumpversion --current-version 0.1.0 minor setup.py ldtk_intgrid_creator/__init__.py