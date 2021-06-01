import request from 'superagent';

const url = ({ path, id }) => `http://localhost:5000/${path}${id ? `/${id}` : ''}`;

const httpRequest = ({ method = 'post', path, id = '', data }) =>
  request(method.toUpperCase(), url({ path, id }))
    .send(data)
    .then((response) => JSON.parse(response.text));

export default httpRequest;
