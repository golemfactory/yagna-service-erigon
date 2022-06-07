import request from 'superagent';
import { Url } from './types';

const url = ({ path, id }: Url) => `/${path}${id ? `/${id}` : ''}`;

type UninitAuthTicket = { status: 'init' | 'pending' };
type InitAuthTicket = {
  status: 'authorized';
  challenge: string;
  response: string;
  account: string;
};
type ErrorAuthTicket = {
  status: 'error';
  error: Error;
};

export type AuthTicket = UninitAuthTicket | InitAuthTicket | ErrorAuthTicket;

export const AUTH_INIT: AuthTicket = { status: 'init' };
export const AUTH_PENDING: AuthTicket = { status: 'pending' };

export type Request = {
  method?: 'get' | 'post';
  path: string;
  id?: string;
  authTicket?: AuthTicket;
  data?: object;
};

export default async function httpRequest({ method = 'post', path, id = '', authTicket, data }: Request) {
  let base = request(method!.toUpperCase(), url({ path, id })).accept('application/json').set('X-Api-Call', '1');
  if (authTicket?.status === 'authorized') {
    base = base.set({
      Message: authTicket.challenge.toString(),
      Signature: authTicket.response.toString(),
      Authorization: `Bearer ${authTicket.account}`,
    });
  }

  const response = await base.send(data);
  return JSON.parse(response.text);
}
