import request from 'superagent';
import {Url} from './types';

const url = ({ path, id }: Url) => `/${path}${id ? `/${id}` : ''}`;

export type AuthTicket =
  | { status: 'init' | 'pending' }
  | {
      status: 'authorized';
      challenge: string;
      response: string;
      account: string;
    };

export type Request = {
    method?: 'get' | 'post';
    path: string;
    id?: string;
    authTicket?: AuthTicket;
    data?: object;
};

export default async function httpRequest({ method = 'post', path, id = '', authTicket, data }: Request) {
  let base = request(method!.toUpperCase(), url({ path, id })).accept('application/json').set('X-Api-Call', '1');
    console.log('auth=', authTicket);
    if (authTicket && authTicket.status === 'authorized') {
        base = base.set({
            'Message': authTicket.challenge.toString(),
            'Signature': authTicket.response.toString(),
            'Authorization': `Bearer ${authTicket.account}`
        });
    }

    const response = await base.send(data);
    return JSON.parse(response.text);
}
