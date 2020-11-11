import os
import pickle
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path) #dotenv 사용해서 env 이용하기

SPORTS_CODE = os.environ['SPORTS_CODE']
TEAM_CODE = os.environ['TEAM_CODE']

SITE_URL = f'http://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode={SPORTS_CODE}&TeamCode={TEAM_CODE}'
LOGIN_URL = 'https://ticket.interpark.com/Gate/TPLogin.asp'

section_names = os.environ.get('SECTION_NAMES').split(",")
print("Target section:", section_names)


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
            if opponent.text != os.environ['OPPONENT']:
                continue

            return time_schedule
    except Exception as e:
        print(e)
        return None

def btn_click(btn):
    btn.send_keys(Keys.ENTER)

def js_function_call_click(btn):
    driver.execute_script('arguments[0].click();', btn)

def click_ticketing_link_for_match(match):
    ticketing_btn = match.find_element_by_class_name('btns').find_element_by_css_selector('a')
    btn_click(ticketing_btn)


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

def switch_to_popup_window(driver):
    child_window = driver.window_handles[-1]
    # 팝업창으로 전환
    try:
        driver.switch_to.window(child_window)
    except Exception as e:
        print(e)

def switch_to_target_iframe(driver, iframe_id):
    while True:
        try:
            target_iframe = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, iframe_id))
            )
            break
        except:
            continue
    driver.switch_to.frame(target_iframe)

def get_next_page(driver):
    driver.switch_to.default_content()
    next_btn = driver.find_element_by_id('SmallNextBtnLink')
    js_function_call_click(next_btn)





options = webdriver.ChromeOptions()
headless = os.environ.get('HEADLESS') == '1'
if headless :
    # 헤드리스 옵션
    options.add_argument('headless')
    # 일반적인 창옵션으로(모바일 반응형을 막기 위해)
    options.add_argument('window-size=1920x1080')
    # gpu 사용하지 않기
    options.add_argument("disable-gpu")
    # 헤드리스 감추기
    ## user-urgent에서 headless 제거
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36")
    # 사용자 언어
    options.add_argument('lang=ko_KR')

#################### 드라이버 구동 ###########################
driver = webdriver.Chrome('./chromedriver', options=options)
###########################################################

if headless :
    # 헤드리스 감추기
    ## 자바스크립트로 가짜 플러그인 리스트 추가
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
    ## 브라우저 언어설정 추가
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")

# ---------------------------------------------------------------



### 드라이버 로그인 ###
login(driver,login_url=LOGIN_URL,site_url=SITE_URL)

# Todo 선예매 인증부 만들기

# 예매하기 버튼 누르기(아직 안열렸으면 새로고침 후 다시 열기)
ticketing_available = False
while not ticketing_available:
    try:
        # 매치 선택
        match = select_match(driver)
        if match is None:
            print("선택한 경기를 찾을 수 없습니다.")

        parent_window = driver.current_window_handle

        click_ticketing_link_for_match(match)
        ticketing_available = True
    except Exception as e:
        print(e)
        time.sleep(2)
        driver.refresh()

switch_to_popup_window(driver)

# 좌석 종류 선택 프레임으로 스위치
switch_to_target_iframe(driver, 'ifrmSeat')

# 좌석 종류 리스트 뽑아오기
wanted_seat_types = os.environ.get('SEAT_TYPES').split(',')
print(wanted_seat_types)
available_seat_types = []
try:
    seat_types = driver.find_elements_by_xpath('/html/body/div/div[3]/div[2]/div[1]/a')
    for seat_type in seat_types:
        seat_type_name = seat_type.get_attribute('sgn')
        if seat_type_name not in wanted_seat_types:
            continue
        left_seat_cnt = seat_type.get_attribute('rc')
        print(seat_type_name, left_seat_cnt)
        if int(left_seat_cnt) > 0 : # Todo 안정성을 위해 조정가능(2나 3 정도로)
            available_seat_types.append(seat_type)
except Exception as e:
    print(e)

# 좌석 종류 선택 후 다음창으로 넘어가기
for seat_type in available_seat_types:
    try:
        btn_click(seat_type)
        select_btn = driver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[3]/a')
        btn_click(select_btn)
        break
    except Exception as e:
        print(e)
        print('해당 좌석 타입이 선택되지 않습니다.')

# 세부 좌석 선택 프레임으로 스위치
switch_to_target_iframe(driver, 'ifrmSeatDetail')

# 세부 좌석 선택
# seats = WebDriverWait(driver, 3).until(
#                 EC.presence_of_all_elements_located((By.CLASS_NAME, 'stySeat'))
#             )
seats = driver.find_elements_by_class_name('stySeat')
selected = False
while not selected:
    for seat in seats:
        try:
            if any(section_name in seat.get_attribute('title') for section_name in section_names): # Todo 원하는 좌석위치
                js_function_call_click(seat)
                selected = True
                break
        except Exception as e:
            print(e)

# 프레임 바꿔서 좌석선택완료 누르기
driver.switch_to.default_content()
switch_to_target_iframe(driver,'ifrmSeat')
selection_complete_btn = driver.find_element_by_xpath('/html/body/form[1]/div/div[1]/div[3]/div/div[4]/a')
btn_click(selection_complete_btn)

## 가격/할인선택
# 가격/할인 option 선택
driver.switch_to.default_content()
switch_to_target_iframe(driver, 'ifrmBookStep')

price_rows = driver.find_elements_by_xpath("//tr[starts-with(@id,'PriceRow']")
print(price_rows.text)

# Todo
# price_tables = driver.find_elements_by_class_name('Tb_price_Wp')
# try:
#     for price_table in price_tables:
#         price_type = price_table.find_element_by_xpath('//tbody/tr/th')
#         if price_type.text == '기본가':
#             price_name = driver.find_element_by_xpath('PriceRow')
#             selected_price_table = price_table
#             break
# except Exception as e:
#     selected_price_table = ''
#     print(e)
# try :
#     options = Select(selected_price_table.find_element_by_xpath("//tbody/tr/td/table/tbody/tr/td[3]/select"))
#     options.select_by_visible_text('1매')  # <- data option 선택
# except Exception as e:
#     print(e)

# Todo 코로나 19 관련 버튼
# Todo 멤버십 인

# 프레임 바꿔서 다음단계 누르기
get_next_page(driver)

## 배송선택/주문자확인
# 예매자 생년월일 입력
switch_to_target_iframe(driver, 'ifrmBookStep')
birth_input = driver.find_element_by_id('YYMMDD')
birth_input.send_keys(os.environ['USER_BIRTH'])

# 프레임 바꿔서 다음단계 누르기
get_next_page(driver)


## 결제하기
switch_to_target_iframe(driver, 'ifrmBookStep')
# 결제방식 뜰 때까지 explicitly wait
try:
     kakaopay = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, 'Payment_22084'))
    )
except Exception as e:
    print(e)
# 카카오 페이 체크
driver.find_element_by_css_selector("input[type='radio'][value='22084']").click() # 왜 되는거야..?
# 프레임 바꿔서 다음 단계 누르기
get_next_page(driver)


## 정보제공동의 창
switch_to_target_iframe(driver, 'ifrmBookStep')
# 정보제공동의 체크박스 뜰 때까지 explicitly wait
try:
      WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'agree_check'))
    )
except Exception as e:
    print(e)
# 필수 체크박스만 체크
try:
    driver.find_element_by_css_selector("input[type='checkbox'][id='CancelAgree']").click()
    driver.find_element_by_css_selector("input[type='checkbox'][id='CancelAgree2']").click()
except Exception as e:
    print(e)
# 프레임 바꿔서 결제하기 버튼 누르기
driver.switch_to.default_content()
next_btn = driver.find_element_by_id('LargeNextBtnLink')
js_function_call_click(next_btn)


## 카카오페이 결제창
switch_to_popup_window(driver)
switch_to_target_iframe(driver, 'kakaoiframe')
# body explicitly wait
WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
try:
    pay_by_message_tab = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/ul/li[2]'))
    )
except Exception as e:
    print(e)
a = pay_by_message_tab.find_element_by_css_selector(".link_gnb").click() # xpath 함부로 사용하지 말자..

phone_num_input = driver.find_element_by_id('userPhone')
phone_num_input.send_keys(os.environ['USER_PHONE'])

birth_input = driver.find_element_by_id('userBirth')
birth_input.send_keys(os.environ['USER_BIRTH'])

pay_ask_btn = driver.find_element_by_class_name('btn_payask')
print(pay_ask_btn.text)
#btn_click(pay_ask_btn)
