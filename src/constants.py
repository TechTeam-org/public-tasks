import os

WF_ENV = os.environ.get("WF_ENV", "dev")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://example.com")
GH_TOKEN = os.environ.get("GH_TOKEN", "xxxxxxxxxx")
GH_PROJECT_ID = os.environ.get("GH_PROJECT_ID", "xxxxxxxxxx")
CREDENTIAL_FILE_PATH = os.environ.get("CREDENTIAL_FILE_PATH", "xxxxxxxxxx")

ASSIGNEE2SLACK_ID = {
    "suguru-toyohara": "U06GE1X4BJ7",
}
