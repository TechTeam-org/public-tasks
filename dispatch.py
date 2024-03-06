import sys
from src.copy_recurring_tasks import create_recurring_tasks
from src.deadline_reporting import deadline_reporting

from loguru import logger
args = sys.argv
app_name = args[1]

match app_name:
    case 'issue_report':
        deadline_reporting()
    case 'copy_recurring':
        create_recurring_tasks()
    case _:
        logger.info("couldn't find application, please set valid app_name")
