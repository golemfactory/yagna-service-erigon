import httpRequest from './httpRequest';

export type AuthProviderType = (message: string) => Promise<string>;
type AuthResult = { message: string; response: string };
type Callback = [(_: AuthResult) => void, (e: Error) => void];

class Resolver {
  authQueue: Array<Callback> = [];
  lastResult: AuthResult | undefined = undefined;
  account: string;
  provider: AuthProviderType;

  constructor(account: string, provider: AuthProviderType) {
    this.account = account;
    this.provider = provider;
  }

  auth(): Promise<{ message: string; response: string }> {
    if (this.lastResult) {
      return Promise.resolve(this.lastResult);
    }
    return new Promise((success, error) => {
      const queue = this.authQueue;
      queue.push([success, error]);
      if (queue.length == 1) {
        this.start();
      }
    });
  }

  start() {
    const provider = this.provider;

    httpRequest({ method: 'get', path: 'getMessage' })
      .then((message) =>
        provider(message)
          .then((response) => {
            this.resolveTo({ message, response });
          })
          .catch((e) => this.reportError(e)),
      )
      .catch((e) => this.reportError(e));
  }

  resolveTo(result: AuthResult) {
    this.lastResult = result;
    for (let it = this.authQueue.pop(); it; it = this.authQueue.pop()) {
      const [success] = it;
      success(result);
    }
  }

  reportError(e: Error) {
    for (let it = this.authQueue.pop(); it; it = this.authQueue.pop()) {
      const [, error] = it;
      error(e);
    }
  }
}

const _resolvers = new Map<string, Resolver>();

export function auth(account: string, provider: AuthProviderType): Promise<{ message: string; response: string }> {
  if (!_resolvers.has(account)) {
    const resolver = new Resolver(account, provider);
    _resolvers.set(account, resolver);
  }
  return _resolvers.get(account)!.auth();
}
