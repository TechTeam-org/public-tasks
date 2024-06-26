from typing import Tuple
from .constants import ASSIGNEE2SLACK_ID, WF_ENV
from .post_slack_message import post_slack_message
from .github_api import get_issues, get_recurring_issues
from loguru import logger
import datetime
import time


def graphql_format(json: dict) -> list[dict[str, str]]:
    """
    GraphQLのレスポンスを整形する
    """
    format_data = []
    nodes = json["data"]["node"]["items"]["nodes"]
    for node in nodes:
        assignees = []
        try:
            due_date = node["deadlines"]["date"]
            issue_url = node["deadlines"]["item"]["content"]["bodyUrl"]
            title = node["deadlines"]["item"]["content"]["title"]
            is_closed = node["deadlines"]["item"]["content"]["closed"]
            if node["deadlines"]["item"]["content"]["assignees"]["nodes"] != []:
                for assignee in node["deadlines"]["item"]["content"]["assignees"]["nodes"]:
                    assignees.append(assignee["login"])
            objective = node["objective"]["name"]
            status = node["status"]["name"]
        except (KeyError, TypeError):
            # 期限が設定されていないIssueはスキップ
            continue
        if is_closed:
            # close済みのIssueはスキップ
            continue
        format_data.append(
            {
                "due_date": due_date,
                "issue_url": issue_url,
                "title": title,
                "assignees": assignees,
                "objective": objective,
                "status": status
            }
        )

    return format_data


def make_report(
    issue_url: str, assignees: list[str], deadline: str, title: str, objective: str
) -> list[dict[str, list] | None]:
    """
    InProgressとTodoのtaskをSlackに送信するレポートメッセージを作成する
    """
    deadline_date = datetime.datetime.strptime(deadline, "%Y-%m-%d")
    today = datetime.datetime.today()
    logger.info(f"Today: {today.strftime('%Y-%m-%d')}")
    logger.info(f"Deadline: {deadline}")
    timedelta = deadline_date - today
    days_to_deadline = timedelta.days + 1
    if days_to_deadline < 0:
        deadline = f"*{abs(days_to_deadline)}日超過！すぐやれ！* :fire:"
    elif days_to_deadline == 0:
        deadline = f"*今日まで* :warning:"
    elif days_to_deadline <= 2:
        deadline = f"*あと{days_to_deadline}日* :warning:"
    else:
        return []
    
    assignee_message = f"*担当者:*"
    for v in assignees:
        try:
            assignee_message += f"\n<@{ASSIGNEE2SLACK_ID[v]}>"
        except KeyError:
            assignee_message += f"\n{v}"
        

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
                            "text": assignee_message,
                        },
                    ],
                },
                {"type": "divider"},
            ]
        }
    ]


def make_slack_messages(format_issues: list[dict[str, str]]) -> list[dict[str, list]]:
    """
        InProgressとTodoとのissueをSlackに連投するメッセージ群を作成する
    """
    if WF_ENV == "dev":
        dev_message = "【テスト通知】"
    else:
        dev_message = ""
    messages = [
        {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🔥締め切り通知{dev_message}🔥",
                        "emoji": True,
                    },
                }
            ]
        }
    ]

    for issue in format_issues:
        messages += make_report(
            issue["issue_url"],
            issue["assignees"],
            issue["due_date"],
            issue["title"],
            issue["objective"],
        )

    if len(messages) == 1:
        messages += [
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "締め切り直前のIssueはありません :yattane:",
                        },
                    }
                ]
            }
        ]

    return messages

def filter_issues(issues: list[dict[str, str]]) -> list[dict[str, str]]:
    rt: list[dict[str,str]] = []
    for issue in issues:
        if issue["status"] == "Done" or issue["status"] == "Review":
            continue
        rt.append(issue)
    return rt


def deadline_reporting():
    """
    メイン処理
    """
    format_issues = graphql_format(get_issues())
    # 完了しているもの出されているものは通知しない
    filtered_issues = filter_issues(format_issues)
    filtered_issues.sort(key=lambda x: x["due_date"])
    messages = make_slack_messages(filtered_issues)
    for message in messages:
        time.sleep(1)
        post_slack_message(message)
