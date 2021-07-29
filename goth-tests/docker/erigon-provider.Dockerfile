ARG YA_CORE_VERSION=0.7.3
ARG YA_RUNTIME_ERIGON_VERSION=0.1.0

FROM ubuntu:latest
ARG YA_CORE_VERSION
ARG YA_RUNTIME_ERIGON_VERSION

RUN apt update \
    && apt install -y supervisor nginx curl


RUN curl -sSfL "https://github.com/golemfactory/yagna/releases/download/v${YA_CORE_VERSION}/golem-provider-linux-v${YA_CORE_VERSION}.tar.gz" \
    | tar -xzf -


RUN mkdir -p "/root/.local/lib/yagna" \
    && mv "golem-provider-linux-v${YA_CORE_VERSION}/plugins" "/root/.local/lib/yagna/plugins" \
    && mv "golem-provider-linux-v${YA_CORE_VERSION}/yagna" "/usr/bin" \
    && mv "golem-provider-linux-v${YA_CORE_VERSION}/ya-provider" "/usr/bin" \
    && mv "golem-provider-linux-v${YA_CORE_VERSION}/golemsp" "/usr/bin" \
    && rm -r "golem-provider-linux-v${YA_CORE_VERSION}"

# TODO: The runtime descriptor should be included in the release package
COPY runtime-descriptor.json /root/.local/lib/yagna/plugins/ya-runtime-erigon.json

RUN curl -sSfL "https://github.com/golemfactory/yagna-service-erigon/releases/download/ya-runtime-erigon-v${YA_RUNTIME_ERIGON_VERSION}/ya-runtime-erigon-v${YA_RUNTIME_ERIGON_VERSION}.tar.gz" \
    | tar -xzf - -C "/root/.local/lib/yagna/plugins"

RUN mkdir -p "/root/.local/share/ya-runtime-erigon"
COPY runtime-config.json /root/.local/share/ya-runtime-erigon/ya-runtime-erigon.json

RUN mkdir -p "/root/.local/share/ya-provider"
COPY globals.json /root/.local/share/ya-provider/globals.json
COPY presets.json /root/.local/share/ya-provider/presets.json

## Touching this file informs Golem installer that terms and conditions are accepted
#RUN mkdir -p "${HOME}/.local/share/ya-installer/terms" \
#    && touch "${HOME}/.local/share/ya-installer/terms/testnet-01.tag"
#
#ADD https://join.golem.network/as-provider ./as-provider.sh
#RUN chmod +x ./as-provider.sh \
#    && ./as-provider.sh
#
# RUN ya-provider preset deactivate wasmtime
# RUN ya-provider preset deactivate vm
# RUN rm "${HOME}/.local/lib/yagna/plugins/ya-runtime-vm.json"
# RUN rm "${HOME}/.local/lib/yagna/plugins/ya-runtime-wasi.json"
#
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# CMD ["/usr/bin/supervisord"]
