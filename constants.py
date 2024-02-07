import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
GH_TOKEN = os.environ.get("GH_TOKEN", "")
GH_PROJECT_ID = os.environ.get("GH_PROJECT_ID", "")

ASSIGNEE2SLACK_ID = {
    "suguru-toyohara": "@豊原優",
}
