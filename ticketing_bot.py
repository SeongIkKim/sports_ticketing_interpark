from selenium import webdriver
import time

SPORTS_CODE = '07004' # 여자배구
TEAM_CODE = 'PV022' # 한국도로공사 # Todo 팀별로 코드 정리


options = webdriver.ChromeOptions()
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

# 헤드리스 감추기
## 자바스크립트로 가짜 플러그인 리스트 추가
driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
## 브라우저 언어설정 추가
driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")


SITE_URL = f'http://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode={SPORTS_CODE}&TeamCode={TEAM_CODE}'

# 사이트 접속
driver.get(SITE_URL)

time.sleep(0.5)

time_schedules = driver.find_elements_by_class_name('timeSchedule')
for time_schedule in time_schedules:
    print(time_schedule.text)

