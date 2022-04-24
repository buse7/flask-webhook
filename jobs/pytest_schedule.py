import os
import json

# get config 
with open('config.json', 'r') as cf:
  config = json.load(cf)

def authCheckerJob():
  os.system(f'python3 -m pytest --slack_username="Auth health check results" --slack_channel=#auth-health-check --slack_hook={config["Slack"]["hook_url"]}  --junitxml=./junit_report.xml')