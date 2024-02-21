from loguru import logger
from .gcp_api import authenticate_with_oidc, access_spreadsheet




def create_recurring_tasks():
    "月初めに定期実行する"
    logger.info("this is reccuring tasks")
    c = authenticate_with_oidc()
    access_spreadsheet(c)
