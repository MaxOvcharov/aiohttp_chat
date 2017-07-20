***The full information in:*** [**DigitalOcean**](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis)

###============= Installing Redis =============

1) Updating system's default application toolset: 
```
sudo apt-get update
apt-get -y upgrade
```
2) Download a compiler with build essential which will help to install Redis from source:
```
sudo apt-get install build-essential
```
3) Download tcl:
```
sudo apt-get install tcl8.5
```
4) Download the latest stable release tarball from Redis.io:
```
cd /usr/src/
wget http://download.redis.io/releases/redis-stable.tar.gz
```
5) Untar it and switch into that directory:
```
tar xzf redis-stable.tar.gz
cd redis-stable
```
6) Run the recommended make test: 
```
make
make test
```
7) Once the program has been installed, Redis comes with a built in
   script that sets up Redis to run as a background daemon: 
```
cd utils
sudo ./install_server.sh
```
8) DO YOUR OWN SETTING FOR CONF FILE:

Selected config:
Port           : 6379
Config file    : /etc/redis/redis_6379.conf
Log file       : /var/log/redis_6379.log
Data dir       : /var/redis/6379
Executable     : /usr/local/bin/redis-server
Cli Executable : /usr/local/bin/redis-cli

9) Added Redis into init.d settings:
```
sudo update-rc.d redis_6379 defaults
```
###============== Managing Redis =================
```
sudo service redis_6379 start
sudo service redis_6379 stop
redis-cli
```