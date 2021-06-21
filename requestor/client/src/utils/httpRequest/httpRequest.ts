import request from 'superagent';
import { HttpRequest, Url } from './types';

const url = ({ path, id }: Url) => `/${path}${id ? `/${id}` : ''}`;

const httpRequest = ({ method = 'post', path, id = '', account, data }: HttpRequest) =>
  request(method.toUpperCase(), url({ path, id }))
    .set({ Authorization: `Bearer ${account}` })
    .send(data)
    .then((response: { text: string }) => JSON.parse(response.text));

export default httpRequest;
