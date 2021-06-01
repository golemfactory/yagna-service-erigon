#!/bin/bash

# Set $ERIGON_HOSTNAME env var

apt-get install -y acl

# setup kvm
curl -sSf -o setup-kvm.sh https://gist.githubusercontent.com/pnowosie/cf0899c34c7588688b82aedff765c605/raw/cf84388c037bc1852e8b2e0cecc76c5e311cff28/setup-kvm.sh
chmod +x ./setup-kvm.sh
sudo ./setup-kvm.sh ubuntu

# Create data dir
mkdir -p /data/erigon/goerli
chown -R ubuntu:ubuntu /data/erigon

setfacl -m u:ubuntu:rw /etc/nginx/erigon_htpasswd

mkdir -p /home/ubuntu/.local/lib/yagna/plugins/ya-runtime-erigon

#==================================================================================================
# Don't run the following as sudo
curl -sSf https://join.golem.network/as-provider | YA_INSTALLER_CORE=pre-rel-v0.7.0-rc5 bash -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# reload .bashrc
# (run the 'golemsp run --payment-network rinkeby')


cat >/home/ubuntu/.local/lib/yagna/plugins/ya-runtime-erigon.json <<EOF
[
  {
    "name": "erigon",
    "version": "0.1.0",
    "supervisor-path": "exe-unit",
    "runtime-path": "ya-runtime-erigon/ya-erigon-runtime",
    "description": "Service wrapper for Erigon (formelly Turbo-Geth)",
    "extra-args": ["--runtime-managed-image"]
  }
]
EOF

cat >/home/ubuntu/.local/share/ya-provider/presets.json <<EOF
{
  "active": [
    "erigon",
    "wasmtime",
    "vm"
  ],
  "presets": [
    {
      "name": "default",
      "exeunit-name": "wasmtime",
      "pricing-model": "linear",
      "usage-coeffs": {
        "duration": 0.1,
        "cpu": 1.0,
        "initial": 1.0
      }
    },
    {
      "name": "erigon",
      "exeunit-name": "erigon",
      "pricing-model": "linear",
      "usage-coeffs": {
        "initial": 0.0,
        "duration": 5.555555555555556e-6,
        "cpu": 0.00002777777777777778
      }
    },
    {
      "name": "vm",
      "exeunit-name": "vm",
      "pricing-model": "linear",
      "usage-coeffs": {
        "duration": 5.555555555555556e-6,
        "cpu": 0.00002777777777777778,
        "initial": 0.0
      }
    },
    {
      "name": "wasmtime",
      "exeunit-name": "wasmtime",
      "pricing-model": "linear",
      "usage-coeffs": {
        "initial": 0.0,
        "duration": 5.555555555555556e-6,
        "cpu": 0.00002777777777777778
      }
    }
  ]
}
EOF


curl -LSf -o ya-erigon-runtime.tar.gz https://github.com/golemfactory/yagna-service-erigon/releases/download/3deaadc/ya-erigon-runtime.tar.gz
tar xvzf ya-erigon-runtime.tar.gz -C /home/ubuntu/.local/lib/yagna/plugins/ya-runtime-erigon

# Configure erigon runtime
mkdir -p /home/ubuntu/.local/share/ya-erigon-runtime

if [[ -z "$ERIGON_HOSTNAME" ]]; then
    read -r -p "hostname: " ERIGON_HOSTNAME
fi

cat >/home/ubuntu/.local/share/ya-erigon-runtime/ya-erigon-runtime.json <<EOF
{
  "public_addr": "https://${ERIGON_HOSTNAME}:8545",
  "data_dir": "/data/erigon",
  "passwd_tool_path": "htpasswd",
  "passwd_file_path": "/etc/nginx/erigon_htpasswd",
  "password_default_length": 15
}
EOF

# start provider in screen :-)
# golemsp run --payment-network rinkeby --subnet erigon
