import pytest
import requests
import re
import allure
import platform
import os
import subprocess
import shutil
import chromedriver_autoinstaller
import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pytest_dependency import DependencyManager
from datetime import datetime, timedelta



# wait set
global timeout 
global now
global nowDate
global nowday
global nextDate
global nextDay

# global variable init
timeout = 5 # wait
now = datetime.now() 
nowDate = now.strftime('%Y-%m-%d')
nowday = now.day
nextDate = (now + timedelta(days=1)).strftime('%Y-%m-%d')
nextDay = (now + timedelta(days=1)).day

# DependencyManager.ScopeCls['module'] = DependencyManager.ScopeCls['session']

# get config 
with open('config.json', 'r') as cf:
  config = json.load(cf)
account = config['ACCOUNT']


# get console parameter
def pytest_addoption(parser):
	parser.addoption("--browser", action="store", dest="browsers", default="chrome", help="Browser Type")
	parser.addoption("--id", action="store", default="", help="id")
	parser.addoption("--password", action="store", default="", help="password")

# multi browser parsing
def pytest_generate_tests(metafunc):
	if 'browser' in metafunc.fixturenames:
		metafunc.parametrize(
			"browser", metafunc.config.option.browsers.split(','), scope='session')

# init browser driver
@pytest.fixture(scope='class')
def selenium_driver(request, browser):
  if browser == 'chrome':
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    try:
      if platform.system() == 'Windows': # check server os * Darwin = Mac
        driver = webdriver.Chrome(service=Service(f"./{chrome_ver}/chromedriver.exe"))
      elif platform.system() == 'Darwin':
        driver = webdriver.Chrome(service=Service(f"./{chrome_ver}/chromedriver"))
    except:
      chromedriver_autoinstaller.install(True)
      if platform.system() == 'Windows': # check server os * Darwin = Mac
        driver = webdriver.Chrome(service=Service(f"./{chrome_ver}/chromedriver.exe"))
      elif platform.system() == 'Darwin':
        driver = webdriver.Chrome(service=Service(f"./{chrome_ver}/chromedriver"))
    
  if browser == 'firefox':
    if platform.system() == 'Windows': # check server os * Darwin = Mac
      driver = webdriver.Firefox(executable_path="./bin/geckodriver.exe")
      driver.implicitly_wait(5)
    elif platform.system() == 'Darwin':
      driver = webdriver.Firefox(executable_path="./bin/geckodriver_mac")
      driver.implicitly_wait(5)

  request.cls.driver = driver
  driver.maximize_window()

  yield driver
  driver.close()

# init google bypass browser(chrome debugging mode)
@pytest.fixture(scope='class')
def selenium_driver_debug(request):
  chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe' if platform.system() == 'Windows' else '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome'
  current_path = os.getcwd() if platform.system() == 'Windows' else '.'
  try:
    shutil.rmtree(rf"{current_path}/chrometemp")  # remove Cookie, Cache files
  except FileNotFoundError:
    pass

  try:
    proc = subprocess.Popen(rf'{chrome_path} --no-first-run --remote-debugging-port=9222 --user-data-dir="{current_path}/chrometemp"', 
                            shell=(False if platform.system() == 'Windows' else True))   # Open the debugger chrome
    
  except FileNotFoundError:
    proc = subprocess.Popen(rf'{chrome_path} --no-first-run --remote-debugging-port=9222 --user-data-dir="{current_path}/chrometemp"', 
                            shell=(False if platform.system() == 'Windows' else True))   # Open the debugger chrome
  
  option = webdriver.ChromeOptions()
  option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

  chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
  try:
    driver = webdriver.Chrome(service=Service(f'./{chrome_ver}/chromedriver.exe'), options=option) if platform.system() == 'Windows' else webdriver.Chrome(service=Service(f'./{chrome_ver}/chromedriver'), options=option)
  except:
    chromedriver_autoinstaller.install(True)
    driver = webdriver.Chrome(service=Service(f'./{chrome_ver}/chromedriver.exe'), options=option) if platform.system() == 'Windows' else webdriver.Chrome(service=Service(f'./{chrome_ver}/chromedriver'), options=option)
  driver.implicitly_wait(10)
  
  request.cls.driver = driver
  driver.maximize_window()

  yield driver
  driver.close()
  driver.quit()  
  proc.kill() # proecess kill
  shutil.rmtree(rf"{current_path}/chrometemp", ignore_errors=True)  # remove Cookie, Cache files

# id args
@pytest.fixture(scope='session')
def id(request):
	return request.config.getoption("--id") if request.config.getoption("--id") else config["DEFAULT"]["ID"]

# password args
@pytest.fixture(scope='session')
def password(request):
	return request.config.getoption("--password") if request.config.getoption("--password") else config["DEFAULT"]["PASSWORD"]


# set up a hook to be able to check if a test has failed
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)

# check if a test has failed
@pytest.fixture(scope="function", autouse=True)
def test_failed_check(request):
    yield
    # request.node is an "item" because we use the default
    # "function" scope
    if request.node.rep_setup.failed:
        print("setting up a test failed!", request.node.nodeid)
    elif request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            driver = request.node.funcargs['selenium_driver' | 'selenium_driver_debug']
            take_screenshot(driver, request.node.nodeid)
            print("executing test failed", request.node.nodeid)

# attach screenshot to allure
def take_screenshot(driver, nodeid):
  test_case_name = re.sub(pattern=r'::|\[', repl='_', string=re.sub(pattern=r'/', repl='_', string=re.sub(pattern=r'https?://|\]', repl='', string=nodeid)))
  allure.attach(driver.get_screenshot_as_png(), name=f'{test_case_name}', attachment_type=allure.attachment_type.PNG)  