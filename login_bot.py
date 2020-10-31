import os
import pickle
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path) #dotenv 사용해서 env 이용하기

driver = webdriver.Chrome('./chromedriver')

url = 'https://ticket.interpark.com/Gate/TPLogin.asp?CPage=B&MN=Y&tid1=main_gnb&tid2=right_top&tid3=login&tid4=login'

driver.get(url)

driver.implicitly_wait(0.5)

driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="loginAllWrap"]/div[2]/iframe'))

InputID = driver.find_element_by_id('userId')
InputID.clear()
InputID.send_keys(os.environ['USER_ID'])

InputPW = driver.find_element_by_name('userPwd')
InputPW.clear()
InputPW.send_keys(os.environ['USER_PASSWORD'])

BtnLogin = driver.find_element_by_id('btn_login')
BtnLogin.send_keys(Keys.ENTER)

c = driver.get_cookies()
with open('cookie.dat', 'wb') as f:
    pickle.dump(c, f)

