# -*- coding: utf-8 -*-

import pytest
import allure
import time
import conftest
import pyautogui
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

@pytest.mark.usefixtures("selenium_driver") # Normal Driver init
class SetUp:
  pass

class TestWebzenLogin(SetUp): # Webzen Account Test Class

  @allure.step('Webzen Login Test Step 1 - Open Login Page')
  def test_MainPageOpen(self): # Main Page -> Login Page Move
    expect_result = 'https://login.webzen.com/Home/Login'
    self.driver.get('https://www.webzen.com')
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//article[@class='main-roll-banner']")))
    self.driver.find_element(By.XPATH, "//a[text() = 'Log In']").click()
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, '//input[@id="Password"]')))
    assert expect_result in self.driver.current_url
      
  @allure.step('Webzen Login Test Step 2 - Login Fail Test')
  def test_WebzenLoginFail(self, id):
    self.driver.find_element(By.ID, "UserID").send_keys(id)
    self.driver.find_element(By.ID, "Password").send_keys('1234')
    self.driver.find_element(By.CLASS_NAME, "btn-auth").click()
    cookie = self.driver.get_cookie("WZ_AUTH")
    assert cookie is None, 'Login Fail Test'

  @allure.step('Webzen Login Test Step 3 - Login Success Test')
  def test_WebzenLoginSuccess(self, id, password):
    self.driver.find_element(By.ID, "UserID").clear()
    self.driver.find_element(By.ID, "Password").clear()
    self.driver.find_element(By.ID, "UserID").send_keys(id)
    self.driver.find_element(By.ID, "Password").send_keys(password)
    self.driver.find_element(By.CLASS_NAME, "btn-auth").click()
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//article[@class='main-roll-banner']")))
    cookie = self.driver.get_cookie("WZ_AUTH")
    assert len(cookie) > 0
      
  @allure.step('Webzen Login Test Step 4 - Logout Test')
  def test_WebzenLogout(self):
    self.driver.find_element(By.XPATH, "//a[@class='nickname']").click()
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//a[@class='nickname selected']")))
    self.driver.find_element(By.XPATH, "//ul[@class='my-contents list']//a[text()='Log Out']").click()
    cookie = self.driver.get_cookie("WZ_AUTH")
    assert cookie is None
      

class TestFacebookLogin(SetUp): # Facebook 3rd Party Test Class
  
  @allure.step('Facebook Login Test Step 1 - Open Login Page')
  def test_LoginPageOpen(self):
    expect_result = 'Log In'
    self.driver.get('https://login.webzen.com/')
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//input[@id='Password']")))
    result = self.driver.find_element(By.XPATH, "//div[contains(@class, 'title')]/h2")
    assert expect_result == result.text
  
  @allure.step('Facebook Login Test Step 2 - Login Success Test')
  def test_FacebookLoginSucess(self):
    self.driver.find_element(By.XPATH, "//a[@class='btn-type btn-facebook']").click()
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.number_of_windows_to_be(2))
    self.driver.switch_to.window(self.driver.window_handles[1])
    self.driver.find_element(By.XPATH, "//input[@id='email']").send_keys(conftest.account['Facebook']['id'])
    self.driver.find_element(By.XPATH, "//input[@id='pass']").send_keys(conftest.account['Facebook']['pwd'])     
    self.driver.find_element(By.XPATH, "//input[@id='pass']").send_keys(Keys.RETURN)
    self.driver.switch_to.window(self.driver.window_handles[0])
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//article[@class='main-roll-banner']")))
    cookie = self.driver.get_cookie("WZ_AUTH")
    assert len(cookie) > 0
      
  @allure.step('Facebook Login Test Step 3 - Logout Test')
  def test_FacebookLogout(self):
    self.driver.find_element(By.XPATH, "//a[@class='nickname']").click()
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//a[@class='nickname selected']")))
    self.driver.find_element(By.XPATH, "//ul[@class='my-contents list']//a[text()='Log Out']").click()
    cookie = self.driver.get_cookie("WZ_AUTH")
    assert cookie is None

@pytest.mark.usefixtures("selenium_driver_debug") # Google login bypass drvier init
class GoogleSetup:
  pass

class TestGoogleLogin(GoogleSetup): # Google 3rd Party Test Class
  @allure.step
  def test_GoogleLoginSucess(self):
    self.driver.get('https://login.webzen.com/')
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//input[@id='Password']")))
    self.driver.find_element(By.XPATH, "//a[@class='btn-type btn-google']").click()
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.number_of_windows_to_be(2)) # wait popup window 
    self.driver.switch_to.window(self.driver.window_handles[1])
    
    time.sleep(3) # wait
    pyautogui.write(conftest.account['Google']['id'])    # Fill in your ID or E-mail
    pyautogui.press('tab', presses=4)   # Press the Tab key 3 times
    pyautogui.press('enter')
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//input[@name='password']")))
    pyautogui.write(conftest.account['Google']['pwd'])   # Fill in your PW
    pyautogui.press('enter')
    
    self.driver.switch_to.window(self.driver.window_handles[0])
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//article[@class='main-roll-banner']")))
    cookie = self.driver.get_cookie("WZ_AUTH")
    assert len(cookie) > 0
      
  @allure.step
  def test_GoogleLogout(self):
    self.driver.find_element(By.XPATH, "//a[@class='nickname']").click()
    WebDriverWait(self.driver, conftest.timeout).until(
      EC.visibility_of_element_located((By.XPATH, "//a[@class='nickname selected']")))
    self.driver.find_element(By.XPATH, "//ul[@class='my-contents list']//a[text()='Log Out']").click()
    cookie = self.driver.get_cookie("WZ_AUTH")
    assert cookie is None
  