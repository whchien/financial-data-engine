# Financial Data Engine

This project shows how to deploy a distributed web scraper for financial data to enhance efficiency, use a relational database for storage, and implement comprehensive monitoring.

## Key Features
1. Distributed Systems: Develop systems using RabbitMQ and Celery for scalable web scraping. 
2. Docker Deployment: Use Docker for streamlined setup and deployment, monitored with Protainer. 
3. Database: Efficiently store and manage data using MySQL. 
4. Monitoring: Implement Grafana, Prometheus for big data monitoring. 
5. Dashboard: Build Grafana dashboards for data status monitoring and anomaly detection.


## Quickstart

Follow these steps to set up and run the distributed web scraper:

### 1. Initial set-up
Clone the repo:
```
git clone https://github.com/whchien/financial-data-engine.git 
```
Install the necessary dependencies:
```
make install-package
```
Initiate docker swarm
```
make init-swarm
```

Create the Docker network for service communication:
```
make create-network
```

### 2. Start Essential Services

Deploy RabbitMQ to handle message queuing:
```
make deploy-rabbitmq
```

Deploy the MySQL service for data storage:
```
make deploy-mysql
```

Set up the MySQL volume for data persistence:
```
make create-mysql-volume
```


### 3. Start Celery Workers

Deploy the Celery worker for TWSE tasks for example:
```
make run-worker-twse
```

### 4. Fetch Financial Data
Send a task to fetch Taiwan futures daily data:
```
make send-taiwan-futures-daily-task
```


By following these steps, you will set up a distributed scraping system capable of efficiently collecting financial data, utilizing RabbitMQ for task queuing, MySQL for data storage, and Celery for task execution.


### Credits
This project is inspired by this [repo](https://github.com/FinMind/FinMindBook).
