ASSETS := $(shell find public)
SOURCES := $(shell find src)

all: build

node_modules: package.json
	yarn install

install: node_modules

build: install $(ASSETS) $(SOURCES)
	yarn build

docker:
	docker build -f docker/Dockerfile . -t erigon-client

clean:
	docker container rm -f erigon-client || true
	docker image rm erigon-client || true
	rm -rf build
	rm -rf node_modules

.PHONY: all install test docker clean
