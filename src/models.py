from dataclasses import dataclass
from loguru import logger
from datetime import datetime
from zoneinfo import ZoneInfo
from croniter import croniter

@dataclass
class SingleSelectedValue:
  option_id: str = ''
  name: str = ''
@dataclass
class Status(SingleSelectedValue):
  pass
  
@dataclass
class Objective(SingleSelectedValue):
  pass

@dataclass
class Issue:
  id: str
  body: str
  title: str
  objective: Objective = None
  assignee: str = ''
  repository: str = ''
  trigger: str = ''
  created_node_id: str = ''
  created_item_id: str = ''
  recurring_end_date: int = 0

  def __init__(self, node: dict):
    content = node["status"]["item"]["content"]
    self.id=content["id"]
    self.body=content["body"]
    self.title=str(content["title"])
    self.repository=content["repository"]["name"]
    if node["cron"] != None:
      self.trigger =  node["cron"].get("text")
    if node["objective"] != None:
      self.objective = Objective(node["objective"].get("optionId"), node["objective"].get("name"))
    if content["assignees"]["nodes"] != []:
      self.assignee = content["assignees"]["nodes"][0][
        "login"
      ] 
    if node["recurring_end_date"] != None:
      self.recurring_end_date = int(node["recurring_end_date"].get("number"))

  def isTodaysTask(self) -> bool:
    if not self.trigger:
      logger.info("cronフォーマットが設定されていません")
      return False
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    try:
      return croniter.match(self.trigger, now)
    except ValueError:
      logger.info(f"適切なcronフォーマットを設定してください, title={self.title}, assignee={self.assignee}, 設定された値={self.trigger}")
      return False
