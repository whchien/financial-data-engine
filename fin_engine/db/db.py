import typing

import pandas as pd
import pymysql
from loguru import logger
from sqlalchemy import engine


def update_to_mysql_with_pandas(df: pd.DataFrame, table: str, mysql_conn: engine.base.Connection) -> bool:
    """Upload data to MySQL using pandas built-in function."""
    if not df.empty:
        try:
            df.to_sql(
                name=table,
                con=mysql_conn,
                if_exists="append",
                index=False,
                chunksize=1000,
            )
        except Exception as e:
            logger.error(f"Failed to upload data to MySQL with pandas: {e}")
            return False
    return True


def update_to_mysql_with_sql(df: pd.DataFrame, table: str, mysql_conn: engine.base.Connection):
    """Upload data to MySQL using raw SQL."""
    sql_statements = build_df_update_sql(table, df)
    commit(sql=sql_statements, mysql_conn=mysql_conn)


def build_update_sql(colnames: typing.List[str], values: typing.List[str]) -> str:
    """Build the SQL statement for updating data."""
    update_sql = ", ".join(
        [f'`{colnames[i]}` = "{values[i]}"' for i in range(len(colnames)) if values[i]]
    )
    return update_sql


def build_df_update_sql(table: str, df: pd.DataFrame) -> typing.List[str]:
    """Build the SQL statements for updating data in MySQL."""
    logger.info("Building SQL statements for DataFrame update")
    sql_statements = []
    for i in range(len(df)):
        row = df.iloc[i]
        values = [pymysql.converters.escape_string(str(v)) for v in row]
        colnames = df.columns.tolist()
        update_sql = build_update_sql(colnames, values)
        sql = f"""
            INSERT INTO `{table}` (`{"`, `".join(colnames)}`)
            VALUES ('{"', '".join(values)}')
            ON DUPLICATE KEY UPDATE {update_sql}
        """
        sql_statements.append(sql)
    return sql_statements


def commit(sql: typing.Union[str, typing.List[str]], mysql_conn: engine.base.Connection):
    """Execute the given SQL statements and commit the transaction."""
    logger.info("Committing SQL transaction")
    trans = mysql_conn.begin()
    try:
        if isinstance(sql, list):
            for statement in sql:
                mysql_conn.execution_options(autocommit=False).execute(statement)
        else:
            mysql_conn.execution_options(autocommit=False).execute(sql)
        trans.commit()
    except Exception as e:
        trans.rollback()
        logger.error(f"Transaction failed and rolled back: {e}")


def query(sql: str, mysql_conn: engine.base.Connection):
    """Execute a query and return the results."""
    result = mysql_conn.execute(sql)
    return result.fetchall()


def upload_data(df: pd.DataFrame, table: str, mysql_conn: engine.base.Connection):
    """Upload data to MySQL, handling duplicate entries appropriately."""
    if not df.empty:
        if not update_to_mysql_with_pandas(df, table, mysql_conn):
            update_to_mysql_with_sql(df, table, mysql_conn)