env:
	virtualenv -p python3 env
install:
	./env/bin/pip install -e .
all: env install