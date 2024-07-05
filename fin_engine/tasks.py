import importlib
import typing

from fin_engine import db
from fin_engine.worker import app, CallbackTask


# Register the task. Only registered tasks can be sent to RabbitMQ.
@app.task(base=CallbackTask)
def crawler(dataset: str, parameters: typing.Dict[str, str]):
    """
    Crawler task to scrape data based on the given dataset and parameters.

    Parameters:
    - dataset: The name of the dataset to scrape.
    - parameters: A dictionary of parameters to pass to the scraper.
    """
    # Use getattr and importlib to dynamically import the scraper module
    scraper_module = importlib.import_module(f"financialdata.scraper.{dataset}")
    scraper = getattr(scraper_module, "scraper")

    # Perform the web scraping
    df = scraper(parameters=parameters)

    # Upload the scraped data to the database
    db.upload_data(df, dataset, db.router.mysql_financialdata_conn)
