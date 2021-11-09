import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen
from urllib.parse import urljoin
import os

# http://kras.incheon.go.kr/land_info/info/landprice/landprice.do?service=landPriceInfo&landcode=2823710100105490078&scale=0

# 데이터 불러옴
cwd = os.getcwd()
file_path = os.path.join(cwd,'data/전처리 파일/부평구 건물 리스트.csv')
building_data = pd.read_csv(file_path)

bupyeong_id = '2823700000'
# 각 동별로 id 넣을것

SEARCH_URL = 'http://kras.incheon.go.kr/land_info/info/landprice/landprice.do' 
BASE_URL = 'http://kras.incheon.go.kr'

with requests.Session() as session:
    res = session.get(BASE_URL)
    bs = BeautifulSoup(res.text,'html.parser')
    form_url = urljoin(BASE_URL,bs.find('form').attrs['action'])
    print(form_url)

    for idx, data in building_data.iterrows():
        input_data = {'sidonm':'인천광역시',
                    'sggnm':data['시군구명'],
                    'umdnm':data['법정읍면동명'],
                    'rinm':'리',
                    'selectLandType_':'일반',
                    'textfield':data['본번'],
                    'textfield2':data['부번']}

        req = session.post(BASE_URL,data=input_data)
        print(req.status_code)

        if req.status_code != 200:
            raise Exception('Not Creat Connection')

        print(req.url)
        res = session.get(req.url)

        bs = BeautifulSoup(res.text,'html.parser')

        row_data = bs.find('tbody').children

        # 반복문을 이용해야 함.
        building_data.iloc[idx,'2017'] = row_data[3].text.strip()
        building_data.iloc[idx,'2018'] = row_data[4].text.strip()
        building_data.iloc[idx,'2019'] = row_data[5].text.strip()

building_data.loc[:,'2017':'2019']