import os

WF_ENV = os.environ.get("WF_ENV", "dev")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
GH_TOKEN = os.environ.get("GH_TOKEN", "")
GH_PROJECT_ID = os.environ.get("GH_PROJECT_ID", "")

ASSIGNEE2SLACK_ID = {
    "suguru-toyohara": "U06GE1X4BJ7",
}
