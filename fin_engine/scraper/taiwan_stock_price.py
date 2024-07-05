import datetime
import time
import typing

import pandas as pd
import requests
from loguru import logger


def is_weekend(date: datetime.date) -> bool:
    """Check if the given date is a weekend (Sunday)."""
    return date.weekday() == 6


def generate_task_parameter_list(start_date: str, end_date: str) -> typing.List[dict]:
    """Generate a list of task parameters, including dates and data sources."""
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    days = (end_date - start_date).days + 1
    date_list = [start_date + datetime.timedelta(days=day) for day in range(days)]

    task_parameters = [
        {"crawler_date": str(date), "data_source": data_source}
        for date in date_list
        for data_source in ["twse", "tpex"]
        if not is_weekend(date)
    ]

    return task_parameters


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data by converting text to numbers."""
    cols_to_clean = ["TradeVolume", "Transaction", "TradeValue", "Open", "Max", "Min", "Close", "Change"]
    for col in cols_to_clean:
        df[col] = (
            df[col].astype(str)
            .str.replace(",", "")
            .str.replace("X", "")
            .str.replace("+", "")
            .str.replace("----", "0")
            .str.replace("---", "0")
            .str.replace("--", "0")
            .str.replace(" ", "")
            .str.replace("除權息", "0")
            .str.replace("除息", "0")
            .str.replace("除權", "0")
        )
    return df


def convert_column_names(df: pd.DataFrame, col_names: typing.List[str]) -> pd.DataFrame:
    """Convert column names from Chinese to English for database storage."""
    column_translation = {
        "證券代號": "StockID",
        "證券名稱": "",
        "成交股數": "TradeVolume",
        "成交筆數": "Transaction",
        "成交金額": "TradeValue",
        "開盤價": "Open",
        "最高價": "Max",
        "最低價": "Min",
        "收盤價": "Close",
        "漲跌(+/-)": "Dir",
        "漲跌價差": "Change",
        "最後揭示買價": "",
        "最後揭示買量": "",
        "最後揭示賣價": "",
        "最後揭示賣量": "",
        "本益比": "",
    }
    df.columns = [column_translation[col] for col in col_names]
    df = df.drop(columns=[""], errors="ignore")
    return df


def twse_header() -> dict:
    """Return the request headers for TWSE website."""
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "www.twse.com.tw",
        "Referer": "https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }


def tpex_header() -> dict:
    """Return the request headers for TPEX website."""
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "www.tpex.org.tw",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }


def set_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Set column names for the DataFrame."""
    df.columns = [
        "StockID", "Close", "Change", "Open", "Max", "Min",
        "TradeVolume", "TradeValue", "Transaction"
    ]
    return df


def crawl_tpex(date: str) -> pd.DataFrame:
    """Crawl TPEX data."""
    logger.info("Crawling TPEX data for date: {}", date)
    url = f"https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={convert_date(date)}&se=AL"
    time.sleep(5)  # Avoid IP ban
    response = requests.get(url, headers=tpex_header())
    data = response.json().get("aaData", [])

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df.iloc[:, [0, 2, 3, 4, 5, 6, 7, 8, 9]]
    df = set_column_names(df.copy())
    df["Date"] = date
    df = clean_data(df.copy())
    return df


def convert_twse_response_to_dataframe(response) -> typing.Tuple[pd.DataFrame, typing.List[str]]:
    """Convert TWSE response to DataFrame."""
    df = pd.DataFrame()
    col_names = []

    try:
        if "data9" in response.json():
            df = pd.DataFrame(response.json()["data9"])
            col_names = response.json()["fields9"]
        elif "data8" in response.json():
            df = pd.DataFrame(response.json()["data8"])
            col_names = response.json()["fields8"]
        elif response.json()["stat"] in ["查詢日期小於93年2月11日，請重新查詢!", "很抱歉，沒有符合條件的資料!"]:
            pass
    except Exception as e:
        logger.error(e)

    return df, col_names


def crawl_twse(date: str) -> pd.DataFrame:
    """Crawl TWSE data."""
    logger.info("Crawling TWSE data for date: {}", date)
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date.replace('-', '')}&type=ALL"
    time.sleep(5)  # Avoid IP ban
    response = requests.get(url, headers=twse_header())
    df, col_names = convert_twse_response_to_dataframe(response)

    if df.empty:
        return pd.DataFrame()

    df = convert_column_names(df.copy(), col_names)
    df["Date"] = date
    df = convert_change(df.copy())
    df = clean_data(df.copy())
    return df


def convert_change(df: pd.DataFrame) -> pd.DataFrame:
    """Convert change column values."""
    logger.info("Converting change column values")
    df["Dir"] = df["Dir"].str.split(">").str[1].str.split("<").str[0]
    df["Change"] = df["Dir"] + df["Change"]
    df["Change"] = df["Change"].str.replace(" ", "").str.replace("X", "").astype(float)
    df = df.fillna("")
    df = df.drop(columns=["Dir"])
    return df


def convert_date(date: str) -> str:
    """Convert date to the required format."""
    logger.info("Converting date: {}", date)
    year, month, day = date.split("-")
    year = int(year) - 1911
    return f"{year}/{month}/{day}"


def crawl(parameters: dict) -> pd.DataFrame:
    """Main crawling function."""
    logger.info("Crawling with parameters: {}", parameters)
    date = parameters.get("crawler_date", "")
    data_source = parameters.get("data_source", "")

    if data_source == "twse":
        return crawl_twse(date)
    elif data_source == "tpex":
        return crawl_tpex(date)
    return pd.DataFrame()
