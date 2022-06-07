# Erigolem client

### Installation

Go to `/client` and in your terminal and type:

```
$ yarn install
```

### Run instructions

In terminal type:

```
$ yarn start
```

This opens [localhost:3000]() the development server.

Instructions for run app in docker are in the main readme file.

### Testing instructions

Go to `/client/e2e` and in your terminal and type:

```
$ docker-compose up --exit-code-from cypress
```

It will run headless test in docker, based on the main dockerfile.

To run test locally, run client and requestor and then:

- For headless mode:

```
$ yarn test:run
```

- For browser mode:

```
$ yarn test:open
```
