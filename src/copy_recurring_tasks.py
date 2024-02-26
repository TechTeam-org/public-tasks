from .github_api import get_recurring_issues, create_issue, register_v2_item, get_fields_info, update_v2_select_field, update_v2_date_field
from loguru import logger
from .models import Issue, Status, Objective
from datetime import datetime, timedelta
import pytz


def graphql_status_format(json: dict, name: str) -> Status | None:
  edges = json["data"]["node"]["fields"]["edges"]
  options: len[dict[str, str]] =[{}]
  for egde in edges:
    try:
      if "name" in egde["node"] and egde["node"]["name"] == "Status":
        options = egde["node"]["options"]
    except TypeError as e:
      # 期限が設定されていないIssueはスキップ
      continue
  for option in options:
    try:
      if option["name"] == name:
        return Status(
          option_id=option["id"],
          name=option["name"], 
          )
    except TypeError as e:
      # 期限が設定されていないIssueはスキップ
      continue
  return None

def graphql_recurring_format(json: dict) -> list[Issue]:
  """
  GraphQLのレスポンスを整形する
  """
  format_data: list[Issue] = []
  nodes = json["data"]["node"]["items"]["nodes"]
  for node in nodes:
    try:
      issue = node["status"]["item"]["content"]
      if node["status"]["name"] == "定期タスク":
        data = Issue(
          id=issue["id"],
          body=issue["body"],
          title=issue["title"],
          repository=issue["repository"]["name"]
          ) 
        if node["cron"] != None:
          data.trigger =  node["cron"].get("text")
        if node["objective"] != None:
          data.objective = Objective(node["objective"].get("optionId"), node["objective"].get("name"))
        if len(issue["assignees"]["nodes"]) > 0:
          data.assignee = issue["assignees"]["nodes"][0][
             "login"
          ] 
        if node["recurring_end_date"] != None:
          data.recurring_end_date = int(node["recurring_end_date"].get("number"))
        format_data.append(data)
    except TypeError as e:
      # 期限が設定されていないIssueはスキップ
      continue
  return format_data

def get_fields_id_map(json:dict) -> dict:
  fields_map: dict[str,str] = {}
  nodes = json["data"]["node"]["fields"]["nodes"]
  for node in nodes:
    if "id" in node:
      fields_map[node["name"]] = node["id"]
  egdes = json["data"]["node"]["fields"]["edges"]
  for egde in egdes:
    if "id" in egde["node"]:
      fields_map[egde["node"]["name"]] = egde["node"]["id"]
  
  return fields_map


def create_recurring_tasks():
    fields_info = get_fields_info()
    target_status = graphql_status_format(fields_info, "Todo")
    # issue取得時にfieldがnullで入っているとfield_idの取得が困難なため始めにmapping
    fields_id_map = get_fields_id_map(fields_info)
    issues = graphql_recurring_format(get_recurring_issues())
    for issue in issues:
      # 取得したcronフォーマットから本日issueを起こすかどうか判別 -> create
      if issue.isTodaysTask():
        create_res = create_issue(issue)
        issue.created_node_id = create_res["node_id"]
        # projectV2へ登録
        register_res = register_v2_item(issue)
        issue.created_item_id = register_res["data"]["addProjectV2ItemById"]["item"]["id"]
        #statusの移動
        update_v2_select_field(issue, fields_id_map["Status"], target_status.option_id)
        #Objectiveが存在した場合update
        if issue.objective != None:
          update_v2_select_field(issue, fields_id_map["Objective"], issue.objective.option_id)
        # 締切日付が存在していた場合update
        if issue.recurring_end_date != 0:
          now = datetime.now( pytz.timezone('Asia/Tokyo'))
          # 指定された日時を計算
          end_date = now + timedelta(days=issue.recurring_end_date)
          update_v2_date_field(issue, fields_id_map["end_date"], end_date.isoformat())
          