import httpRequest from './httpRequest';

export type AuthProviderType = (message: string) => Promise<string>;
type AuthResult = { message: string; response: string };
type Callback = [(_: AuthResult) => void, (e: Error) => void];
const authQueue: Array<Callback> = [];

export function auth(provider: AuthProviderType): Promise<{ message: string; response: string }> {
  const result: Promise<{ message: string; response: string }> = new Promise((success, error) => {
    authQueue.push([success, error]);
  });
  if (authQueue.length > 1) {
    return result;
  }
  httpRequest({ method: 'get', path: 'getMessage' })
    .then((message) =>
      provider(message).then((response) => {
        let it = authQueue.pop();
        while (it) {
          const [success] = it;
          success({ message, response });
          it = authQueue.pop();
        }
      }),
    )
    .catch((e) => {
      for (let it = authQueue.pop(); it; it = authQueue.pop()) {
        const [, error] = it;
        error(e);
      }
    });
  return result;
}
