import os

WF_ENV = os.environ.get("WF_ENV", "dev")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://example.com")
GH_TOKEN = os.environ.get("GH_TOKEN", "xxxxxxxxxx")
GH_PROJECT_ID = os.environ.get("GH_PROJECT_ID", "xxxxxxxxxx")

ASSIGNEE2SLACK_ID = {
    "suguru-toyohara": "U06GE1X4BJ7",
    "leo-KaiD": "U06EMEJP09Z",
    "Daiki-Ishii": "U06E72K31ST",
    "m-chiaki": "U06EJLVG869",
}