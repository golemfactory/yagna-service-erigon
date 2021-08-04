FROM node:16 as builder

WORKDIR /client
COPY src ./src
COPY public ./public
COPY package.json .
COPY tsconfig.json .
COPY yarn.lock .
RUN yarn install && yarn build

FROM nginx:latest

COPY --from=builder /client/build /var/www

COPY docker/default.conf.template /etc/nginx/conf.d
COPY docker/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
