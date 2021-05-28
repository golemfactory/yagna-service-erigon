#!/bin/bash

die() {
    echo "$1" >&2
    exit 1
}

[[ "$(id -u)" == 0 ]] || die "Please run as root"

if [[ -z "$ERIGON_HOSTNAME" ]]; then
    read -r -p "hostname: " ERIGON_HOSTNAME
fi

# ========= nginx & certbot =========

apt-get install -y nginx certbot apache2-utils

# stop nginx to leave port 80 for certbot standalone
systemctl stop nginx

[[ -f /etc/nginx/dhparam.pem ]] || \
    openssl dhparam -out /etc/nginx/dhparam.pem 2048

if [[ ! -f /etc/letsencrypt/live/$ERIGON_HOSTNAME/fullchain.pem ]]; then
    if [[ -z "$ERIGON_EMAIL" ]]; then
        read -r -p "email (for certbot): " ERIGON_EMAIL
    fi

    certbot certonly --standalone -d "$ERIGON_HOSTNAME" --email "$ERIGON_EMAIL" -n --agree-tos --force-renewal
fi

cat >/etc/letsencrypt/renewal-hooks/post/nginx-reload.sh <<EOF
#!/bin/bash
nginx -t && systemctl reload nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/post/nginx-reload.sh

touch /etc/nginx/erigon_htpasswd
# TODO: give access to golem user to modify passwords
# setfacl -m u:golem:rw /etc/nginx/erigon_htpasswd

cat >/etc/systemd/system/reload-nginx.path <<EOF
[Unit]
[Unit]
Description=Watch for changes in nginx config
After=local-fs.target

[Path]
Unit=reload-nginx.service
PathChanged=/etc/nginx/erigon_htpasswd

[Install]
WantedBy=default.target
EOF

cat >/etc/systemd/system/reload-nginx.service <<EOF
[Unit]
Description=Reload nginx
Requisite=nginx.service
Wants=local-fs.target
After=nginx.service

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl reload nginx

[Install]
WantedBy=default.target
EOF

systemctl daemon-reload

cat >/etc/nginx/nginx.conf <<EOF
# Based on config generated by nginxconfig.io
# https://www.digitalocean.com/community/tools/nginx?domains.0.server.domain=&domains.0.server.documentRoot=&domains.0.server.redirectSubdomains=false&domains.0.https.forceHttps=false&domains.0.https.hstsSubdomains=false&domains.0.php.php=false&domains.0.reverseProxy.reverseProxy=true&domains.0.reverseProxy.proxyPass=http%3A%2F%2F127.0.0.1%3A8545&domains.0.routing.root=false&domains.0.routing.index=index.html&domains.0.routing.fallbackHtml=true&global.https.ocspCloudflare=false&global.https.ocspGoogle=false&global.https.ocspOpenDns=false&global.tools.modularizedStructure=false

user                 www-data;
pid                  /run/nginx.pid;
worker_processes     auto;
worker_rlimit_nofile 65535;

# Load modules
include              /etc/nginx/modules-enabled/*.conf;

events {
    multi_accept       on;
    worker_connections 65535;
}

http {
    charset                utf-8;
    sendfile               on;
    tcp_nopush             on;
    tcp_nodelay            on;
    server_tokens          off;
    log_not_found          off;
    types_hash_max_size    2048;
    types_hash_bucket_size 64;
    client_max_body_size   16M;

    # MIME
    include                mime.types;
    default_type           application/octet-stream;

    # Logging
    access_log             /var/log/nginx/access.log;
    error_log              /var/log/nginx/error.log warn;

    # SSL
    ssl_session_timeout    1d;
    ssl_session_cache      shared:SSL:10m;
    ssl_session_tickets    off;

    # Diffie-Hellman parameter for DHE ciphersuites
    ssl_dhparam            /etc/nginx/dhparam.pem;

    # Mozilla Intermediate configuration
    ssl_protocols          TLSv1.2 TLSv1.3;
    ssl_ciphers            ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    # OCSP Stapling
    ssl_stapling           on;
    ssl_stapling_verify    on;

    # Connection header for WebSocket reverse proxy
    map \$http_upgrade \$connection_upgrade {
        default upgrade;
        ""      close;
    }

    # Load configs
    include /etc/nginx/conf.d/*.conf;

    # example.com
    server {
        listen                               8545 ssl http2;
        listen                               [::]:8545 ssl http2;
        server_name                          $ERIGON_HOSTNAME;

        # SSL
        ssl_certificate                      /etc/letsencrypt/live/$ERIGON_HOSTNAME/fullchain.pem;
        ssl_certificate_key                  /etc/letsencrypt/live/$ERIGON_HOSTNAME/privkey.pem;
        ssl_trusted_certificate              /etc/letsencrypt/live/$ERIGON_HOSTNAME/chain.pem;

        # security headers
        add_header X-XSS-Protection          "1; mode=block" always;
        add_header X-Content-Type-Options    "nosniff" always;
        add_header Referrer-Policy           "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy   "default-src 'self' http: https: data: blob: 'unsafe-inline'; frame-ancestors 'self';" always;
        add_header Strict-Transport-Security "max-age=31536000" always;

        auth_basic                           "erigon";
        auth_basic_user_file                 erigon_htpasswd;

        # reverse proxy
        location / {
            proxy_pass                         http://127.0.0.1:8545;
            proxy_http_version                 1.1;
            proxy_cache_bypass                 \$http_upgrade;

            # Proxy headers
            proxy_set_header Upgrade           \$http_upgrade;
            proxy_set_header Connection        \$connection_upgrade;
            proxy_set_header Host              \$host;
            proxy_set_header X-Real-IP         \$remote_addr;
            proxy_set_header X-Forwarded-For   \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_set_header X-Forwarded-Host  \$host;
            proxy_set_header X-Forwarded-Port  \$server_port;

            # Proxy timeouts
            proxy_connect_timeout              60s;
            proxy_send_timeout                 60s;
            proxy_read_timeout                 60s;
        }

        # gzip
        gzip            on;
        gzip_vary       on;
        gzip_proxied    any;
        gzip_comp_level 6;
        gzip_types      text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;
    }
}
EOF

nginx -t || die "nginx doesn't like it's config"
systemctl restart nginx
systemctl enable --now reload-nginx.path