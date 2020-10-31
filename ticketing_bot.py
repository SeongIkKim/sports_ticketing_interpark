import os
import pickle
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SPORTS_CODE = '07004' # 여자배구
TEAM_CODE = 'PV022' # 한국도로공사 # Todo 팀별로 코드 정리
OPPONENT = 'GS 칼텍스' # 상대팀 - GS 칼텍스 - 화면에 나오는 그대로 적어야함
SITE_URL = f'http://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode={SPORTS_CODE}&TeamCode={TEAM_CODE}'
LOGIN_URL = 'https://ticket.interpark.com/Gate/TPLogin.asp'

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path) #dotenv 사용해서 env 이용하기


def save_cookies(driver, location):
    c = driver.get_cookies()
    with open(location, 'wb') as f:
        pickle.dump(c, f)

def load_cookies(driver, location, url=None):
    if os.path.getsize(location) > 0:
        cookies = pickle.load(open(location, "rb"))
        driver.delete_all_cookies()
        driver.get(SITE_URL)
        for cookie in cookies:
            driver.add_cookie(cookie)

def delete_cookies(driver, domains=None):

    if domains is not None:
        cookies = driver.get_cookies()
        original_len = len(cookies)
        for cookie in cookies:
            if str(cookie["domain"]) in domains:
                cookies.remove(cookie)
        if len(cookies) < original_len:  # if cookies changed, we will update them
            # deleting everything and adding the modified cookie object
            driver.delete_all_cookies()
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        driver.delete_all_cookies()

def select_match(driver):
    '''
    여러개의 경기 리스트 중 원하는 팀의 경기를 선택
    :param driver: 지금 사용하는 웹드라이버
    :return: 정상적일경우 time_schedule html객체, 그렇지 않을 경우 None
    '''
    try:
        time_schedules = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "timeSchedule"))
        )
        for time_schedule in time_schedules:
            opponent = time_schedule.find_element_by_class_name('team2')

            # 찾던 경기가 아니면 다른 time_schedule 탐색
            if opponent.text != OPPONENT:
                continue

            return time_schedule
    except Exception as e:
        print(e)
        return None

def get_link_for_match(time_schedule):
    ticketing_btn = time_schedule.find_element_by_class_name('btns').find_element_by_css_selector('a')
    ticketing_btn.send_keys(Keys.ENTER)

def login(driver, login_url, site_url):
    driver.get(login_url)
    driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="loginAllWrap"]/div[2]/iframe'))

    InputID = driver.find_element_by_id('userId')
    InputID.clear()
    InputID.send_keys(os.environ['USER_ID'])

    InputPW = driver.find_element_by_name('userPwd')
    InputPW.clear()
    InputPW.send_keys(os.environ['USER_PASSWORD'])

    BtnLogin = driver.find_element_by_id('btn_login')
    BtnLogin.send_keys(Keys.ENTER)

    driver.get(site_url)








options = webdriver.ChromeOptions()
# # 헤드리스 옵션
# options.add_argument('headless')
# # 일반적인 창옵션으로(모바일 반응형을 막기 위해)
# options.add_argument('window-size=1920x1080')
# # gpu 사용하지 않기
# options.add_argument("disable-gpu")
# # 헤드리스 감추기
# ## user-urgent에서 headless 제거
# options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36")
# # 사용자 언어
# options.add_argument('lang=ko_KR')

#################### 드라이버 구동 ###########################
driver = webdriver.Chrome('./chromedriver', options=options)
###########################################################

# # 헤드리스 감추기
# ## 자바스크립트로 가짜 플러그인 리스트 추가
# driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
# ## 브라우저 언어설정 추가
# driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")

# ---------------------------------------------------------------



#### 쿠키생성 ####
login(driver,login_url=LOGIN_URL,site_url=SITE_URL)

# 매치 선택
match = select_match(driver)
if match is None:
    print("선택한 경기를 찾을 수 없습니다.")

# 예매하기 버튼 누르기
get_link_for_match(match)

print('끝')





