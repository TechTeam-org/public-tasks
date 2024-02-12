import sys
from src.recurring_task import create_recurring_tasks
from src.deadline_reporting import deadline_reporting

from loguru import logger

ISSUE_REPORT_NAME='issue_report'
RECURRING_TASKS_NAME='recurring_tasks'
args = sys.argv
app_name = args[1]

if app_name == ISSUE_REPORT_NAME:
    deadline_reporting()
elif app_name == RECURRING_TASKS_NAME:
    create_recurring_tasks()
else:
    logger.info("couldn't find application, please set valid app_name")
