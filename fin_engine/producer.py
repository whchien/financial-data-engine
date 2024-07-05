import importlib
import sys

from fin_engine.tasks import crawler
from loguru import logger


def update(dataset: str, start_date: str, end_date: str):
    """
    Update dataset by generating task parameters and sending tasks to the crawler.

    Parameters:
    - dataset: Name of the dataset to update.
    - start_date: The start date for data retrieval in YYYY-MM-DD format.
    - end_date: The end date for data retrieval in YYYY-MM-DD format.
    """
    # Import the module and get the parameter list generator function
    module = importlib.import_module(f"financialdata.crawler.{dataset}")
    gen_task_parameter_list = getattr(module, "gen_task_paramter_list")

    # Generate the list of parameters for the crawling tasks
    parameter_list = gen_task_parameter_list(start_date=start_date, end_date=end_date)

    # Loop through the parameters and send the tasks
    for parameters in parameter_list:
        logger.info(f"Dataset: {dataset}, Parameters: {parameters}")
        task = crawler.s(dataset=dataset, parameters=parameters)

        # Send the task to the specified queue
        task.apply_async(queue=parameters.get("data_source", ""))


if __name__ == "__main__":
    dataset, start_date, end_date = sys.argv[1:]
    update(dataset, start_date, end_date)
