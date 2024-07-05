import time
import typing

from loguru import logger
from sqlalchemy import engine
from fin_engine.db import clients


def check_alive(connection: engine.base.Connection):
    """Check if the database connection is alive by executing a simple query."""
    connection.execute("SELECT 1 + 1")


def check_connect_alive(connection: engine.base.Connection, connect_func: typing.Callable) -> engine.base.Connection:
    """Check if the connection is alive, and if not, attempt to reconnect."""
    if connection:
        try:
            check_alive(connection)
            return connection
        except Exception as e:
            logger.info(f"{connect_func.__name__} reconnect, error: {e}")
            time.sleep(1)
            try:
                connection = connect_func()
            except Exception as e:
                logger.info(f"{connect_func.__name__} connect error, error: {e}")
            return check_connect_alive(connection, connect_func)


class Router:
    def __init__(self):
        self._mysql_financialdata_conn = clients.get_mysql_financialdata_conn()
        self._mysql_monitor_conn = clients.get_mysql_monitor_conn()

    def check_mysql_financialdata_conn_alive(self) -> engine.base.Connection:
        """Check and maintain the MySQL financial data connection."""
        self._mysql_financialdata_conn = check_connect_alive(
            self._mysql_financialdata_conn,
            clients.get_mysql_financialdata_conn,
        )
        return self._mysql_financialdata_conn

    def check_mysql_monitor_conn_alive(self) -> engine.base.Connection:
        """Check and maintain the MySQL monitor connection."""
        self._mysql_monitor_conn = check_connect_alive(
            self._mysql_monitor_conn,
            clients.get_mysql_monitor_conn,
        )
        return self._mysql_monitor_conn

    @property
    def mysql_financialdata_conn(self) -> engine.base.Connection:
        """Property to get the MySQL financial data connection."""
        return self.check_mysql_financialdata_conn_alive()

    @property
    def mysql_monitor_conn(self) -> engine.base.Connection:
        """Property to get the MySQL monitor connection."""
        return self.check_mysql_monitor_conn_alive()

    def close_connection(self):
        """Close the MySQL financial data connection."""
        self._mysql_financialdata_conn.close()
