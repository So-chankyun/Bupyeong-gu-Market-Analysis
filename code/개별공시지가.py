from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import ElementNotInteractableException
import os
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time

start = time.time()
temp_time = start

main_url = 'http://kras.incheon.go.kr/land_info/info/landprice/landprice.do'

options = webdriver.ChromeOptions()
options.add_argument('headless') # headless모드
options.add_argument('window-size=1920x1080') 
options.add_argument('--log-level=3') # 이 코드가 없으면 headless 모드시 log가 많이 표시된다.

options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

driver = webdriver.Chrome('C:\\chromedriver',chrome_options=options)
driver.get(main_url)

def component_load(driver,data):
    timeout = 10
    # 컴포넌트를 로드하고 데이터를 입력함.
    time.sleep(0.3)
    sggnm = WebDriverWait(driver,timeout).until(EC.presence_of_element_located((By.ID,'sggnm')))
    sggnm.send_keys('부평구')

    time.sleep(0.3)
    umdnm = WebDriverWait(driver,timeout).until(EC.presence_of_element_located((By.ID,'umdnm')))      
    umdnm.send_keys(data['법정읍면동명'])
    
    # 본번, 지번을 입력할 때는 clear하고 입력.
    bonbeon = WebDriverWait(driver,timeout).until(EC.presence_of_element_located((By.ID,'textfield')))
    bubeon = WebDriverWait(driver,timeout).until(EC.presence_of_element_located((By.ID,'textfield2')))

    bonbeon.clear()
    bubeon.clear()

    bonbeon.send_keys(data['본번'])
    bubeon.send_keys(data['부번'])

    print('지번 : {0}-{1}'.format(data['본번'],data['부번']))
    
def Alert_exception(driver):
    not_found_data = driver.switch_to.alert
    msg = not_found_data.text
    print(msg)
    not_found_data.accept()

    # 개별공시지가 조회 실패 오류 시에만 새로 로딩
    if "개별공시지가 조회 실패" in msg:
        driver.get(main_url)
        time.sleep(5)
    elif "선택하신 지번이 검색되지 않았습니다. 다시 확인하여 주시기 바랍니다." in msg:
        raise NoAlertPresentException
    
    return True

def save(old_data, new_data):
    Int_col = list(old_data) + list(new_data)
    Int_dict_col = {}

    for i, col in enumerate(list(old_data)):
        Int_col[i+1] = col

    old_data = pd.concat([old_data,new_data.reset_index()],axis=1)
    old_data.rename(columns=Int_dict_col,inplace=True)
    old_data.drop(['Unnamed: 0','index','idx'],axis=1,inplace=True)
    old_data.to_csv(os.path.join(cwd,'data/전처리 파일/건물 개별공시가격.csv'),index=False)
    print('저장완료')
    
# 검색에 사용할 데이터 로딩
file_path = '../data/전처리 파일/부평구 건물 리스트.csv'
result_file_path = 'C:\\Data Analysis\\부평구 상권분석\\data\\전처리 파일\\건물 개별공시가격.csv'
use_data = result_file_path
building_data = pd.read_csv(result_file_path,encoding='utf-8')
crawling_data = pd.DataFrame()

# 2017에 값이 없는 데이터들의 인덱스를 추출
zero_index = building_data[building_data['2017'].isnull()].index

# 건물 데이터 한줄씩 실행하여 정보 입력하기 
for idx, data in building_data.iterrows():
    # nan index list에 idx가 없다면 이미 데이터가 있는것이므로 다음으로 진행
    if idx not in zero_index:
        continue
    
    while True:
        try:
            component_load(driver,data)
            driver.find_element_by_xpath('//*[@id="searching"]/a').click()

            # alert가 발생한다면
            if Alert_exception(driver):
                continue

        except StaleElementReferenceException : 
            # 컴포넌트를 다시 받아올 수 있도록 재실행.
            print('StaleElementReferenceException')
            continue
        except ElementNotInteractableException :
            print('ElementNotInteractableException')
            continue
        except NoAlertPresentException as ie:
            break

    # 반복문 탈출 후 조회 사이트로 이동
    price_data = {'2017': 0,'2018':0,'2019':0} # 디폴트 값 지정
    year = {'2017','2018','2019'} # 추출 연도 지정

    # 클릭 후 해당 컴포넌트가 나올때까지 기다림
    table_tbody = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#main-container > div.cont > table > tbody')))  
    row_data = table_tbody.find_elements_by_tag_name('tr')
    # 4,5,6행이 17~19년 정보이다.
    
    if len(row_data) < 4:
        # 테이블의 row가 4보다 작으면 19년까지의 데이터가 없는 것이다.
        print('No Data')
    else:
        # 2017~2019년 개별공시지가 데이터 저장
        # 데이터가 있어도 해당 연도인지 확인하고 저장.
        max = len(row_data) if len(row_data) < 6 else 6 

        for i in range(3,max):
            price = row_data[i].find_elements_by_tag_name('td')

            if price[0].text in year:
                price_data[price[0].text] = price[3].text
        
        # 개별공시지가 데이터 저장
        temp = pd.DataFrame.from_dict([{'idx':idx,
                                    '2017':price_data['2017'],
                                    '2018':price_data['2018'],
                                    '2019':price_data['2019']}])

        # 원본데이터일 경우
        if use_data == file_path:
            crawling_data = pd.concat([crawling_data,temp],axis=0)

        # 결과데이터일 경우
        else:
            building_data.iloc[idx,7] = price_data['2017']
            building_data.iloc[idx,8] = price_data['2018']
            building_data.iloc[idx,9] = price_data['2019']

        print(temp)

    # 진행률 출력
    level = (idx / len(building_data))*100
    print('진행률 : {0:.2f}%\n'.format(level))

    # 5분마다 저장
    if (time.time()-temp_time) > 60:
        temp_time = time.time()
        print('경과시간 : {:.2f}분'.format((time.time()-start) / 60))
        # save(building_data,crawling_data)
        building_data.to_csv(result_file_path,index=False)
        print('저장완료')

driver.quit()
# save(building_data,crawling_data)
building_data.to_csv(result_file_path,index=False)







