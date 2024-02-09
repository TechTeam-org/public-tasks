from .constants import WEBHOOK_URL
from slack_sdk import WebhookClient
from loguru import logger


def post_slack_message(message: dict) -> None:
    webhook = WebhookClient(WEBHOOK_URL)
    response = webhook.send(blocks=message["blocks"])
    if response.status_code != 200:
        logger.error("Failed to send message")
        logger.error(f"slack response code: {response.status_code}")
        logger.error(f"slack response body: {response.body}")
        raise Exception("Failed to send message")
    else:
        logger.info(f"slack response code: {response.status_code}")
        logger.info(f"slack response body: {response.body}")
