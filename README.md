### Simple chat with aiohttp + socket.io

#### 1) Generate SSL certificate and configuration of nginx:

##### For python 2.x.x
```
sudo apt-get install python-pip python-dev nginx
```

##### For Python 3.x.x
```
sudo apt-get install python3-pip python3-dev nginx
```

##### Install Let's Encrypt
```
sudo apt-get install letsencrypt
```

##### Add lines to the file /etc/nginx/sites-available/default
```
location ~ /.well-known {
                allow all;
        }
```

##### Change root path on <path_to_your_project> in the
##### file /etc/nginx/sites-available/default
```
root /etc/nginx/sites-available/default
```

##### Check Nginx settings
```
sudo nginx -t
sudo systemctl restart nginx
```

##### Before you starting generate certificate,
##### you have to configure DNS on yours hosting with yours domain name.
```
sudo letsencrypt certonly -a webroot --webroot-path=/<!!! path_to_your_project !!!> -d <!!! www.example.com !!!>
```

##### You can find yours pub certificate and privet key in directory

```
sudo ls -l /etc/letsencrypt/live/your_domain_name
```

##### Generate strong Diffie-Hellman group
```
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
sudo ls -lah /etc/ssl/certs/dhparam.pem
```

##### Create Nginx snippet for yours pub certificate and privet key
```
sudo vim /etc/nginx/snippets/ssl-<!!! example.com !!!>.conf
```
with this rows
```
ssl_certificate /etc/letsencrypt/live/<!!! example.com !!!>/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/<!!! example.com !!!>/privkey.pem;
```

##### Create Nginx snippet for yours strong Diffie-Hellman group
```
sudo vim /etc/nginx/snippets/ssl-params.conf
```
with this rows
```
# from https://cipherli.st/
# and https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html

ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
ssl_ecdh_curve secp384r1;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
# Disable preloading HSTS for now.  You can use the commented out header line that includes
# the "preload" directive if you understand the implications.
#add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;

ssl_dhparam /etc/ssl/certs/dhparam.pem;
```

##### After that you should change configuration in nginx.conf with
##### yours settings. Than you can use init.sh script for deploy this project
```
sudo chmod 777 init.sh
./init.sh --help
./init.sh --start
```

#### 2)Install Supervisor
```
sudo apt-get install -y supervisor
```

