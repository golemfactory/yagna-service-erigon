import request from 'superagent';
import { HttpRequest, Url } from './types';

const url = ({ path, id }: Url) => `http://localhost:5000/${path}${id ? `/${id}` : ''}`;

const httpRequest = ({ method = 'post', path, id = '', data }: HttpRequest) =>
  request(method.toUpperCase(), url({ path, id }))
    .send(data)
    .then((response: { text: string }) => JSON.parse(response.text));

export default httpRequest;
