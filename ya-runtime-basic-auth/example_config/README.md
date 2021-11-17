# Example configuration of Basic-Auth runtime

Here we will present example configuration of the Golem provider tool `golemsp`
that serves 2 authentication runtimes for `erigon` and `lighthouse` clients.

## Directory structure

You can find following files in this directory. Bellow we explain them in more details

```bash
├── plugins
│  ├── ya-runtime-erigon.json
│  └── ya-runtime-lhouse.json
├── ya-provider
│  └── presets.json
├── ya-runtime-erigon
│  └── ya-runtime-erigon.json
└── ya-runtime-lhouse
   └── ya-runtime-lhouse.json
```

### 1. Yagna plugins

In this directory plugin's bianries and descriptors are placed.

Directory tree may looks like bellow:
```bash
~/.local/lib/yagna/plugins
├── exe-unit
├── ya-runtime-basic-auth
│  └── ya-runtime-basic-auth
├── ya-runtime-erigon.json
├── ya-runtime-lhouse.json
├── ya-runtime-vm
│  ├── runtime
│  │  ├── ...
│  └── ya-runtime-vm
├── ya-runtime-vm.json
├── ya-runtime-wasi
└── ya-runtime-wasi.json
```

### 2. Provider's preset.json file

The `preset.json` file is located in `~/.local/share/ya-provider/` directory.
It's overwritten by `golemsp` (TODO: more info needed)

### 3. Runtime configuration files

The `golemsp` tool loads plugins and search for the configuration files in `~/.local/share/<runtime-name>/<runtime-name>.json` 
In this directory we present sample configuration of `ya-runtime-erigon` and `ya-runtime-lhouse` runtimes.

