from .github_api import get_recurring_issues, create_issue, register_v2_item, get_fields, update_v2_select_field, update_v2_date_field
from .models import Issue, Status
from datetime import datetime, timedelta
import pytz


def graphql_status_format(json: dict, name: str) -> Status:
  """
  fieldの中から引数で指定したStatus(Option)を取得
  """
  edges = json["data"]["node"]["fields"]["edges"]
  options: len[dict[str, str]] =[]
  for edge in edges:
    try:
      if edge["node"]["name"] == "Status":
        options = edge["node"]["options"]
        break
    except (KeyError, TypeError):
      # 　nameが取得できなかった場合を想定しskip
      continue
  for option in options:
    try:
      if option["name"] == name:
        return Status(
          option_id=option["id"],
          name=option["name"], 
          )
    except (KeyError, TypeError):
      # 期限が設定されていないIssueはスキップ
      continue
  return Status()

def graphql_recurring_format(json: dict) -> list[Issue]:
  """
  GraphQLのレスポンスを整形する
  """
  format_data: list[Issue] = []
  nodes = json["data"]["node"]["items"]["nodes"]
  for node in nodes:
    try:
      if node["status"]["name"] == "定期タスク":
        data = Issue(node)
        format_data.append(data)
    except (TypeError, KeyError):
      # 期限が設定されていないIssueはスキップ
      continue
  return format_data

def get_fields_id_map(json:dict) -> dict:
  """
  fieldのidとnameをmapping
  """
  fields_map: dict[str,str] = {}
  nodes = json["data"]["node"]["fields"]["nodes"]
  for node in nodes:
    if "id" in node:
      fields_map[node["name"]] = node["id"]
  egdes = json["data"]["node"]["fields"]["edges"]
  for edge in egdes:
    if "id" in edge["node"]:
      fields_map[edge["node"]["name"]] = edge["node"]["id"]
  
  return fields_map


def create_recurring_tasks():
    """
    定期タスクの自動追加メイン処理
    """
    fields_info = get_fields()
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
          