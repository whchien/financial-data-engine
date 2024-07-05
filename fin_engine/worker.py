import importlib
import socket
import time
import typing

import pymysql
from loguru import logger

from celery import Celery, Task
from fin_engine import db
from fin_engine.config import (
    MESSAGE_QUEUE_HOST,
    MESSAGE_QUEUE_PORT,
    WORKER_ACCOUNT,
    WORKER_PASSWORD,
)


class CallbackTask(Task):
    def retry_task(self, **kwargs):
        """Retry the task if it fails."""
        logger.info(f"Retrying task with kwargs: {kwargs}")
        scraper = getattr(importlib.import_module("fin_engine.tasks"), "scraper")
        dataset = kwargs.get("dataset")
        parameters = kwargs.get("parameters")
        task = scraper.s(dataset=dataset, parameters=parameters)
        task.apply_async(queue=parameters.get("data_source", ""))

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task succeeded: {task_id}")
        return super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the failure and retry the task."""
        logger.error(f"Task failed: {task_id}, Exception: {exc}")

        sql = """
            INSERT INTO `celery_log` (
                `retry`, `status`, `worker`, `task_id`, `msg`, `info`, `args`, `kwargs`
            ) VALUES (
                '0', '-1', '{}', '{}', '{}', '{}', '{}', '{}'
            )
        """.format(
            socket.gethostname(),
            task_id,
            pymysql.converters.escape_string(str(exc)),
            pymysql.converters.escape_string(str(einfo)),
            pymysql.converters.escape_string(str(args)),
            pymysql.converters.escape_string(str(kwargs)),
        )

        db.commit(sql=sql, mysql_conn=db.router.mysql_financialdata_conn)

        logger.info(f"Task arguments: {args}")
        logger.info(f"Task keyword arguments: {kwargs}")

        self.retry_task(kwargs)
        time.sleep(3)

        return super().on_failure(exc, task_id, args, kwargs, einfo)


broker_url = f"pyamqp://{WORKER_ACCOUNT}:{WORKER_PASSWORD}@{MESSAGE_QUEUE_HOST}:{MESSAGE_QUEUE_PORT}/"
app = Celery(
    "task",
    include=["fin_engine.tasks"],
    broker=broker_url,
)
