from loguru import logger
from constants import WEBHOOK_URL
from slack_sdk import WebhookClient
import json

message = {
    "blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "締め切り通知",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "<https://github.com/TechTeam-org/public-tasks/issues/4|#4 2024年02月29日の資料作成をする>"
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*締め切り:*\n今日中"
				},
				{
					"type": "mrkdwn",
					"text": "*担当者:*\nsuguru-toyohara"
				}
			]
		},
		{
			"type": "divider"
		}
	]
}

webhook = WebhookClient(WEBHOOK_URL)
response = webhook.send(text="test", blocks=message["blocks"])
logger.info(response.status_code)
logger.info(response.body)


