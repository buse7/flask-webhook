import json


with open('config.json', 'r') as cf:
  config = json.load(cf)

def parser_jira_user_to_slack(data):
  return 0

# slack parser
def parser_jira_to_slack(data):
  payload = {
  "channel" : "jira-notification",
  "username": "Jira",
  "icon_url" : config["Jira"]["icon"],
  	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"<{config['Jira']['prefix_url']+data['issue']['key']}|{data['issue']['key']}> | *{data['issue']['fields']['summary']}* - {data['issue_event_type_name']}"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"*Assign* : {data['issue']['fields']['assignee']}",
			},
		},
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*Description* : {data['issue']['fields']['description']}"
      }
    },
    {
      "type": "divider"
    }
	],
  }
  return payload


