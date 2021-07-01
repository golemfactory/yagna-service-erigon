# Erigolem
Erigon node as a Golem service

The purpose of this example is to demonstrate building a Golem service using a dedicated, self-contained runtime. It features an Ethereum network client, Erigon (f.k.a. Turbo-geth) started on provider nodes on user's demand. Interaction with the service, once it's running and its location and credentials have been passed to the requestor, is *not* facilitated by Golem though.

---

The application consist of three major components:

1. **User interface** (`client/`)  
   A browser-based interface written in TypeScript using [React](https://reactjs.org/). It allows the end user to interact with the application, i.e. start an Erigon node after authenticating with their [Metamask](https://metamask.io/) wallet, and later manage their node(s).
2. **Requestor server** (`requestor/`)  
   A Python application developed using [Quart](https://pgjones.gitlab.io/quart/) and [yapapi-service-manager](https://github.com/golemfactory/yapapi-service-manager). It acts both as an HTTP server (handling requests from the user interface), and as a requestor agent (submitting tasks to the Golem network).
3. **Erigon runtime** (`ya-runtime-erigon/`)  
    A dedicated, self-contained runtime created with [ya-runtime-sdk](https://github.com/golemfactory/ya-runtime-sdk). It is a Rust binary wrapping [Erigon](https://github.com/ledgerwatch/erigon) service itself so that it can be orchestrated by yagna daemon. The runtime also controls the access to the service by managing [Nginx](https://www.nginx.com/) configuration.

Instructions how to run and test the requestor server are [here](https://github.com/golemfactory/yagna-service-erigon/blob/master/requestor/README.md).

Full project documentation can be found in the [Golem handbook](https://handbook.golem.network/requestor-tutorials/service-development/service-example-2-managed-erigon).
