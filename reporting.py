from constants import GH_TOKEN, WEBHOOK_URL, GH_PROJECT_ID, ASSIGNEE2SLACK_ID
from slack_sdk import WebhookClient
from loguru import logger
from jinja2 import Template
import datetime
import requests
import time


def graphql_format(json: dict) -> list[dict[str, str]]:
    """
    GraphQLのレスポンスを整形する
    """
    format_data = []
    nodes = json["data"]["node"]["items"]["nodes"]
    for node in nodes:
        try:
            due_date = node["deadlines"]["date"]
            issue_url = node["deadlines"]["item"]["content"]["bodyUrl"]
            title = node["deadlines"]["item"]["content"]["title"]
            assignee = node["deadlines"]["item"]["content"]["assignees"]["nodes"][0][
                "login"
            ]
            objective = node["objective"]["name"]
        except TypeError:
            # 期限が設定されていないIssueはスキップ
            continue
        format_data.append(
            {
                "due_date": due_date,
                "issue_url": issue_url,
                "title": title,
                "assignee": assignee,
                "objective": objective,
            }
        )

    return format_data


def get_issues() -> dict:
    """
    GraphQLを使ってGitHubProjectからIssue情報を取得する
    """
    headers = {"Authorization": f"bearer {GH_TOKEN}"}
    url = "https://api.github.com/graphql"
    query_template = """
    {
      node(id: "{{ PROJECT_ID}}" ){
        ... on ProjectV2 {
          items(first: 100){
            nodes {
              objective: fieldValueByName(name: "Objective"){
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                }
              }
              deadlines: fieldValueByName(name: "end_date"){
                ... on ProjectV2ItemFieldDateValue {
                  date
                  item {
                    ... on ProjectV2Item{
                      content {
                        ... on Issue{
                          bodyUrl
                          title
                          assignees(first: 1){
                            nodes{
                              login
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    query = Template(query_template).render(PROJECT_ID=GH_PROJECT_ID)
    response = requests.post(url, json={"query": query}, headers=headers)
    if response.status_code != 200 or "errors" in response.json().keys():
        logger.error("Failed to get issues")
        logger.error(response.json())
        raise Exception("Failed to get issues")
    else:
        logger.info(f"Github Response Code: {response.status_code}")
        return response.json()


def make_report(
    issue_url: str, assignee: str, deadline: str, title: str, objective: str
) -> list[dict[str, list] | None]:
    """
    Slackに送信するレポートメッセージを作成する
    """
    deadline_date = datetime.datetime.strptime(deadline, "%Y-%m-%d")
    today = datetime.datetime.today()
    timedelta = deadline_date - today
    days_to_deadline = timedelta.days + 1
    if days_to_deadline < 0:
        deadline = f"*{abs(days_to_deadline)}日超過！すぐやれ！* :fire:"
    elif days_to_deadline == 0:
        deadline = f"*今日まで* :warning:"
    else:
        return []

    try:
        slack_mention = f"<@{ASSIGNEE2SLACK_ID[assignee]}>"
    except KeyError:
        slack_mention = assignee

    return [
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"【{objective}】<{issue_url}|{title}>",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*締め切り:*\n{deadline}"},
                        {
                            "type": "mrkdwn",
                            "text": f"*担当者:*\n{slack_mention}",
                        },
                    ],
                },
                {"type": "divider"},
            ]
        }
    ]


def make_slack_messages(format_issues: list[dict[str, str]]) -> list[dict[str, list]]:
    """
    Slackに連投するメッセージ群を作成する
    """
    messages = [
        {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔥締め切り通知🔥",
                        "emoji": True,
                    },
                }
            ]
        }
    ]

    for issue in format_issues:
        messages += make_report(
            issue["issue_url"],
            issue["assignee"],
            issue["due_date"],
            issue["title"],
            issue["objective"],
        )

    if messages == []:
        messages += [
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "締め切り直前のIssueはありません :バンザイ:",
                        },
                    }
                ]
            }
        ]

    return messages


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


def main():
    """
    メイン処理
    """
    format_issues = graphql_format(get_issues())
    format_issues.sort(key=lambda x: x["due_date"])
    messages = make_slack_messages(format_issues)
    for message in messages:
        time.sleep(1)
        post_slack_message(message)


if __name__ == "__main__":
    main()
