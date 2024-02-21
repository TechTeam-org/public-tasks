from loguru import logger



def create_recurring_tasks():
    "月初めに定期実行する"
    logger.info("this is reccuring tasks")
    authenticate_with_oidc()
