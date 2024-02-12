import sys
from src.deadline_reporting import deadline_reporting
from loguru import logger



args = sys.argv
app_name = args[0]

if app_name == 'issue_report':
    deadline_reporting()
else:
    logger.info("couldn't find application, please set valid app_name")
    
