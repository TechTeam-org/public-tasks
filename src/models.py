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
