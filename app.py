import json
import atexit
import re
import os
import requests
import helpers.payload_parser as payload_parser
import jobs.pytest_schedule as pytest_schedule
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, Response

app = Flask(__name__)

# config set
with open('config.json', 'r') as cf:
  config = json.load(cf)

# scheduler setting
scheduler = BackgroundScheduler()
scheduler.add_job(func=pytest_schedule.authCheckerJob, trigger="interval", seconds=1)
# scheduler.start()

atexit.register(lambda: scheduler.shutdown())

@app.route('/', methods=['GET', 'POST'])
def index():
  print('Success!')
  print(request)
  return 'Working...'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():  
  if request.method == 'GET':
    print('get')
  elif request.method == 'POST':
    source = request.get_json()
    response = requests.post(config['Slack']['hook_url'], json=payload_parser.parser_jira_to_slack(source), headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
      raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text)
    )
  return 'hi'

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
  