***The full information in:*** [**DigitalOcean**](https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-rabbitmq)
### ============== Installing RabbitMQ ===============

1) Updating system's default application toolset:
```
apt-get update
apt-get -y upgrade
```
2) Enable RabbitMQ application repository:
```
echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list
```
3) Add the verification key for the package:
```
curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -
```
4) Update the sources with our new addition from above:
```
apt-get update
```
5) install RabbitMQ:
```
sudo apt-get install rabbitmq-server
```
6) In order to manage the maximum amount of connections upon launch, 
   open up and edit the following configuration file 
   (Uncomment the limit line (i.e. remove #) before saving):
```
sudo vim /etc/default/rabbitmq-server
```

### ======== Enabling the Management Console =========

1) Enable RabbitMQ Management Console
```
sudo rabbitmq-plugins enable rabbitmq_management
```
2) Run RabbitMQ Management Console on brouser
   The default username and password are both set “guest” for the log in.
```
http://[your droplet's IP]:15672/
```

### ============== Managing RabbitMQ =================

1) To start the service:
```
service rabbitmq-server start
```
2) To stop the service:
```
service rabbitmq-server stop
```
3) To restart the service:
```
service rabbitmq-server restart
```
4) To check the status:
```
service rabbitmq-server status
```

### == How to Create a Cluster On a Single Machine ===

1) sudo -i
2) Make sure that you don’t have a /etc/rabbitmq/rabbitmq.config
3) RABBITMQ_NODE_PORT=5673 RABBITMQ_SERVER_START_ARGS="-rabbitmq_management listener [{port,15673}]" RABBITMQ_NODENAME=<YOUR_NODE_NAME> rabbitmq-server
4) rabbitmqctl -n <YOUR_NODE_NAME> status
5) rabbitmqctl -n <YOUR_NODE_NAME> stop_app
6) rabbitmqctl -n <YOUR_NODE_NAME> reset
7) rabbitmqctl -n <YOUR_NODE_NAME> join_cluster rabbit@`hostname -s`
8) rabbitmqctl -n <YOUR_NODE_NAME> start_app
9) rabbitmqctl cluster_status