import datetime
import io
import time
import typing

import pandas as pd
import requests


def futures_header() -> dict:
    """Request header parameters to mimic a browser when browsing the website."""
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "101",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.taifex.com.tw",
        "Origin": "https://www.taifex.com.tw",
        "Pragma": "no-cache",
        "Referer": "https://www.taifex.com.tw/cht/3/dlFutDailyMarketView",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
    }


def colname_zh2en(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names from Chinese to English for easier database storage."""
    colname_dict = {
        "交易日期": "date",
        "契約": "FuturesID",
        "到期月份(週別)": "ContractDate",
        "開盤價": "Open",
        "最高價": "High",
        "最低價": "Low",
        "收盤價": "Close",
        "漲跌價": "Change",
        "漲跌%": "ChangePercent",
        "成交量": "Volume",
        "結算價": "SettlementPrice",
        "未沖銷契約數": "OpenInterest",
        "交易時段": "TradingSession",
    }
    df = df.drop(
        ["最後最佳買價", "最後最佳賣價", "歷史最高價", "歷史最低價", "是否因訊息面暫停交易", "價差對單式委託成交量"],
        axis=1,
    )
    df.columns = [colname_dict.get(col, col) for col in df.columns]
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data."""
    df["date"] = df["date"].str.replace("/", "-")
    df["ChangePercent"] = df["ChangePercent"].str.replace("%", "")
    df["ContractDate"] = df["ContractDate"].astype(str).str.replace(" ", "")
    if "TradingSession" in df.columns:
        df["TradingSession"] = df["TradingSession"].map({"一般": "Regular", "盤後": "AfterMarket"})
    else:
        df["TradingSession"] = "Regular"

    numeric_columns = [
        "Open", "High", "Low", "Close", "Change", "ChangePercent",
        "Volume", "SettlementPrice", "OpenInterest"
    ]
    df[numeric_columns] = df[numeric_columns].replace("-", "0").astype(float)
    df = df.fillna(0)
    return df


def fetch_futures_data(date: str) -> pd.DataFrame:
    """Fetch futures data from the exchange website."""
    url = "https://www.taifex.com.tw/cht/3/futDataDown"
    form_data = {
        "down_type": "1",
        "commodity_id": "all",
        "queryStartDate": date.replace("-", "/"),
        "queryEndDate": date.replace("-", "/"),
    }
    time.sleep(5)  # Sleep to avoid IP ban
    response = requests.post(url, headers=futures_header(), data=form_data)
    if response.ok and response.content:
        df = pd.read_csv(io.StringIO(response.content.decode("big5")), index_col=False)
        return df
    return pd.DataFrame()


def generate_date_parameters(start_date: str, end_date: str) -> typing.List[dict]:
    """Generate a list of date parameters."""
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    days = (end_date - start_date).days + 1
    return [{"crawler_date": str(start_date + datetime.timedelta(days=day)), "data_source": "taifex"} for day in
            range(days)]


def crawler(parameters: dict) -> pd.DataFrame:
    """Main crawler function."""
    date = parameters.get("crawler_date", "")
    df = fetch_futures_data(date)
    if df.empty:
        return df
    df = colname_zh2en(df)
    df = clean_data(df)
    return df
