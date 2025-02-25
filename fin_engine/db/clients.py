from fin_engine.config import (
    MYSQL_DATA_USER,
    MYSQL_DATA_PASSWORD,
    MYSQL_DATA_HOST,
    MYSQL_DATA_PORT,
    MYSQL_DATA_DATABASE,
    MYSQL_MONITOR_USER,
    MYSQL_MONITOR_PASSWORD,
    MYSQL_MONITOR_HOST,
    MYSQL_MONITOR_PORT,
    MYSQL_MONITOR_DATABASE,
)
from sqlalchemy import create_engine, engine


def get_mysql_financialdata_conn() -> engine.base.Connection:
    """Get a connection to the MySQL financial data database."""
    address = (
        f"mysql+pymysql://{MYSQL_DATA_USER}:{MYSQL_DATA_PASSWORD}"
        f"@{MYSQL_DATA_HOST}:{MYSQL_DATA_PORT}/{MYSQL_DATA_DATABASE}"
    )
    engine = create_engine(address)
    connection = engine.connect()
    return connection


def get_mysql_monitor_conn() -> engine.base.Connection:
    """Get a connection to the MySQL monitor database."""
    address = (
        f"mysql+pymysql://{MYSQL_MONITOR_USER}:{MYSQL_MONITOR_PASSWORD}"
        f"@{MYSQL_MONITOR_HOST}:{MYSQL_MONITOR_PORT}/{MYSQL_MONITOR_DATABASE}"
    )
    engine = create_engine(address)
    connection = engine.connect()
    return connection
