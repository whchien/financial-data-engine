# Financial Data Engine

This project shows how to deploy a distributed web scraper for financial data to enhance efficiency, use a relational database for storage, and implement comprehensive monitoring.

## Key Features
- Distributed Systems: Develop systems using RabbitMQ and Celery for scalable web scraping. 
- Docker Deployment: Use Docker for streamlined setup and deployment.
- Database Management: Efficiently store and manage data using MySQL.
- Monitoring Systems: Implement Grafana, Prometheus for big data monitoring.
- Dashboard Creation: Build Grafana dashboards for data status monitoring and anomaly detection.


### Commands

#### Start RabbitMQ
```sh
make deploy-rabbitmq
```

#### Install packages
```sh
make install-package
```

#### Create network
```sh
make create-network
```

#### Create MySQL volume
```sh
make create-mysql-volume
```

#### Start MySQL
```sh
make deploy-mysql
```

#### Start Celery - TWSE
```sh
make run-worker-twse
```

#### Start Celery - TPEX
```sh
make run-worker-tpex
```

#### Start Celery - TAIFEX
```sh
make run-worker-taifex
```

#### Send Taiwan stock price task
```sh
make send-taiwan-stock-price-task
```

#### Send Taiwan futures daily task
```sh
make send-taiwan-futures-daily-task
```

#### Generate dev environment variables
```sh
make gen-dev-env-variable
```


### Credits
This project is inspired by the repo: https://github.com/FinMind/FinMindBook