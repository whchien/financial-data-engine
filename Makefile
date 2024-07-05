CI_COMMIT_SHORT_SHA := $(shell git rev-parse --short=8 HEAD)

init-swarm:
	docker swarm init

deploy-portainer:
	docker stack deploy -c portainer.yml por

deploy-rabbitmq:
	docker stack deploy -c rabbitmq.yml rabbitmq

create-network:
	docker network create --driver=overlay my_network

create-mysql-volume:
	docker volume create mysql

deploy-mysql:
	docker stack deploy -c mysql.yml mysql

install-package:
	pipenv sync

run-worker-twse:
	pipenv run celery -A financialdata.worker worker --loglevel=info --concurrency=1  --hostname=%h.twse -Q twse

run-worker-tpex:
	pipenv run celery -A financialdata.worker worker --loglevel=info --concurrency=1  --hostname=%h.tpex -Q tpex

run-worker-taifex:
	pipenv run celery -A financialdata.worker worker --loglevel=info --concurrency=1  --hostname=%h.taifex -Q taifex

sent-taiwan-stock-price-task:
	pipenv run python financialdata/producer.py taiwan_stock_price 2021-04-01 2021-04-12

sent-taiwan-futures-daily-task:
	pipenv run python financialdata/producer.py taiwan_futures_daily 2021-04-01 2021-04-12

gen-dev-env-variable:
	python genenv.py

gen-staging-env-variable:
	VERSION=STAGING python genenv.py

gen-release-env-variable:
	VERSION=RELEASE python genenv.py

build-image:
	docker build -f Dockerfile -t linsamtw/class01_crawler:dev .

push-image:
	docker push linsamtw/class01_crawler:dev

deploy-crawler-worker:
	docker stack deploy -c crawler_worker.yml crawler_worker

deploy-crawler-scheduler:
	docker stack deploy -c crawler_scheduler.yml crawler_scheduler

build-grafana-image:
	SHA=${CI_COMMIT_SHORT_SHA} docker-compose -f grafana.yml build --no-cache

deploy-grafana: build-grafana-image
	SHA=${CI_COMMIT_SHORT_SHA} docker stack deploy -c grafana.yml grafana