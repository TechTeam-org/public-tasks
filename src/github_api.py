import requests
from constants import GH_PROJECT_ID, GH_TOKEN
from jinja2 import Template
from loguru import logger

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

