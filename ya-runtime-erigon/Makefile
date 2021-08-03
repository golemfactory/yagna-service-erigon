.PHONY: clean arm64

arm64:
	docker run -it --rm \
		--workdir /git-repo \
		--volume $(shell pwd):/git-repo \
		--volume /etc/passwd:/etc/passwd \
		--env HOST_USER=`id -u`:`id -g` \
		golemfactory/build-aarch64:0.1.1 \
		bash -c 'cargo build --release && chown -R $$HOST_USER ./target'

clean:
	rm -rf target
