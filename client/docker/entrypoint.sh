#!/usr/bin/env sh
# Solution copied from https://serverfault.com/a/919212
set -eu

if [ -z "$API_URL" ]; then
  echo "API_URL not set"
  exit 1
fi

envsubst '${API_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

exec "$@"
