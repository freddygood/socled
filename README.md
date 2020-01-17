# Sockled Thumbnails application

## Requirements

Python 2.7
pip
virtualenv
git
ffmpeg

#### Ubuntu

```
apt-get update && \
apt-get install -y python-dev python-pip python-virtualenv git ffmpeg
```

### Clone-and-start

#### Clone repo and install packages

```
set -e
mkdir -p /var/lib/socled
cd /var/lib/socled
git clone --depth 1 https://github.com/freddygood/socled.git app
cd app
virtualenv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

#### Configure the application

```
cat <<EOF > /var/lib/socled/app/config.py
thumbnails_url = 'http://example.com'
EOF
```


### Start the application manually

```
cd /var/lib/socled/app
. venv/bin/activate
uwsgi --ini uwsgi.ini
```

### Start the application

#### systemd (Ubuntu 16) / RHEL7 / CentOS7

```
cp -v /var/lib/socled/app/socled.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable socled.service
systemctl start socled.service
```

#### upstart (Ubuntu 14)

```
cp /var/lib/socled/app/socled.conf /etc/init/
start socled
```

### Restart the application

#### systemd

```
systemctl restart auth_token.service
```

#### upstart

```
restart auth_token.service
```

### Reload the configuration (graceful restart)

#### systemd

```
systemctl reload auth_token.service
```

#### upstart

```
reload auth_token.service
```

### Configure nginx

#### upstream configuration

```
upstream thumbnails {
    server 127.0.0.1:8080;
}
```

#### cache directory

```
uwsgi_cache_path /var/cache/nginx/thumbnails levels=1:1 use_temp_path=off keys_zone=thumbnails:1m max_size=1g inactive=24h;
```

#### thumbnails location

```
location = /transcoderthumbnail {
    include uwsgi_params;
    uwsgi_pass thumbnails;
    uwsgi_cache thumbnails;
    uwsgi_cache_key $request_uri;
}
```
