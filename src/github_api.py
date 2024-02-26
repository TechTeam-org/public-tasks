from .constants import GH_PROJECT_ID, GH_TOKEN, GH_OWNER
from .models import Issue, Status
from jinja2 import Template
from loguru import logger
import requests
import json

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
                          closed
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

def get_fields_info() -> dict:
  """
  GraphQLを使ってGitHubProjectからIssue情報を取得する
  """
  headers = {"Authorization": f"bearer {GH_TOKEN}"}
  url = "https://api.github.com/graphql"
  query_template = """
    {
      node(id: "{{PROJECT_ID}}") {
        ... on ProjectV2 {
          fields(first: 100) { # 10は取得するフィールドの数、必要に応じて変更してください
            nodes{
                ... on ProjectV2Field{
                    id
                    name
                }
            }
            edges {
              node {
                ... on ProjectV2SingleSelectField {
                  id
                  name
                  options {
                    id
                    name
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
      logger.error("Failed to get status")
      logger.error(response.json())
      raise Exception("Failed to get fields")
  else:
      logger.info(f"Github Response Code: {response.status_code}")
      return response.json()

def get_recurring_issues() -> dict:
    """
    GraphQLを使ってGitHubProjectからIssue情報を取得する
    """
    headers = {"Authorization": f"bearer {GH_TOKEN}"}
    url = "https://api.github.com/graphql"
    query_template = """
    {
      node(id: "{{PROJECT_ID}}") {
        ... on ProjectV2 {
          title
          items(first: 100) {
            nodes {
              status: fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    item {
                    ... on ProjectV2Item{
                      content {
                        ... on Issue{
                          id
                          body
                          title
                          assignees(first: 1){
                            nodes{
                              login
                            }
                          }
                          repository {
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
              cron:fieldValueByName(name: "cron") {
                ... on ProjectV2ItemFieldTextValue {
                  id
                  text
                }
              }
              recurring_end_date:fieldValueByName(name: "recurring_end_date") {
                ... on ProjectV2ItemFieldNumberValue {
                  id
                  number
                }
              }
              objective: fieldValueByName(name: "Objective"){
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  optionId
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
        raise Exception("Failed to get recurring issues")
    else:
        logger.info(f"Github Response Code: {response.status_code}")
        return response.json()

def create_issue(issue: Issue) -> dict:

  headers = {
    "Authorization": f"bearer {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
  }
  url = f"https://api.github.com/repos/{GH_OWNER}/{issue.repository}/issues"
  payload = {
    "title": issue.title,
    "body": issue.body,
    "assignee": issue.assignee
  }
  response = requests.post(url, json=payload, headers=headers)
  if response.status_code != 201 or "errors" in response.json().keys():
      logger.error("Failed to create issues")
      logger.error(response.json())
      raise Exception("Failed to create issues")
  else:
      logger.info(f"Github Response Code: {response.status_code}")
      return response.json()
  
def register_v2_item(issue: Issue):
  """
  GraphQLを使ってGitHubProjectからIssue情報を取得する
  """
  headers = {"Authorization": f"bearer {GH_TOKEN}"}
  url = "https://api.github.com/graphql"
  mutation_template = """
    mutation {
      addProjectV2ItemById(input: {
        projectId: "{{ PROJECT_ID }}",
        contentId: "{{ node_id }}"
      }) {
        item {
        id
      }
    }
  }
  """
  query = Template(mutation_template).render(PROJECT_ID=GH_PROJECT_ID, node_id=issue.created_node_id)
  response = requests.post(url, json={"query": query}, headers=headers)
  if response.status_code != 200 or "errors" in response.json().keys():
      logger.error("Failed to register v2 item")
      logger.error(response.json())
      raise Exception("Failed to register v2 item")
  else:
      logger.info(f"Github Response Code: {response.status_code}")
      return response.json()

def update_v2_select_field(issue: Issue, field_id: str, option_id: str):
  """
  GraphQLを使ってGitHubProjectからIssue情報を取得する
  """
  headers = {"Authorization": f"bearer {GH_TOKEN}"}
  url = "https://api.github.com/graphql"
  mutation_template = """
   mutation {
      updateProjectV2ItemFieldValue(input: {
        fieldId: "{{field_id}}"
        itemId: "{{item_id}}"
        projectId: "{{PROJECT_ID}}"
        value: {singleSelectOptionId:"{{option_id}}"}
      }) {
        projectV2Item {
        id
      }
    }
  }
  """
  query = Template(mutation_template).render(
      field_id=field_id,
      item_id=issue.created_item_id,
      PROJECT_ID=GH_PROJECT_ID,
      option_id=option_id)
  response = requests.post(url, json={"query": query}, headers=headers)
  if response.status_code != 200 or "errors" in response.json().keys():
      logger.error("Failed to update v2 item")
      logger.error(response.json())
      raise Exception("Failed to update v2 item")
  else:
      logger.info(f"Github Response Code: {response.status_code}")
      return response.json()
  
def update_v2_date_field(issue: Issue, field_id: str, end_date: str):
  """
  GraphQLを使ってGitHubProjectからIssue情報を取得する
  """
  headers = {"Authorization": f"bearer {GH_TOKEN}"}
  url = "https://api.github.com/graphql"
  mutation_template = """
   mutation {
      updateProjectV2ItemFieldValue(input: {
        fieldId: "{{field_id}}"
        itemId: "{{item_id}}"
        projectId: "{{PROJECT_ID}}"
        value: {date:"{{date}}"}
      }) {
        projectV2Item {
        id
      }
    }
  }
  """
  query = Template(mutation_template).render(
      field_id=field_id,
      item_id=issue.created_item_id,
      PROJECT_ID=GH_PROJECT_ID,
      date=end_date)
  response = requests.post(url, json={"query": query}, headers=headers)
  if response.status_code != 200 or "errors" in response.json().keys():
      logger.error("Failed to update v2 item")
      logger.error(response.json())
      raise Exception("Failed to update v2 item")
  else:
      logger.info(f"Github Response Code: {response.status_code}")
      return response.json()