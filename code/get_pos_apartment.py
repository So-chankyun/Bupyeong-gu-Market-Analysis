import numpy as np
import pandas as pd
from urllib.request import urlopen
from urllib import parse
from urllib.request import Request
from urllib.error import HTTPError

from bs4 import BeautifulSoup
import json
import os

# naver api
client_id = 'mncjy4lf5z'
client_pw = 's82zIti8a9u7g6CzlEajqgcgHdIhwTfvh8pPXdJN'

api_url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query='

# 주소 목록 파일
apart_data = pd.read_csv('./data/전처리 파일/부평구 아파트 위치(위경도 포함).csv',encoding='utf-8')
null_data = apart_data[apart_data['latitude'].isnull()]
null_data.loc[:,'소재지지번주소'] = null_data.loc[:,'소재지지번주소'].apply(lambda x : x.split('-')[0])

# 네이버 지도 API 이용해서 위경도 찾기
def find_position(addresses):
    geo_coordi = []
    # data = addresses.tolist()
    data = addresses
    for idx, row in data.iterrows():
        add_urlenc = parse.quote(row['소재지지번주소'])
        url = api_url + add_urlenc
        request = Request(url)
        request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
        request.add_header('X-NCP-APIGW-API-KEY', client_pw)
        try:
            response = urlopen(request)
        except HTTPError as e:
            print('HTTP Error!')
            latitude = None
            longitude = None
        else:
            rescode = response.getcode()
            if rescode == 200:
                response_body = response.read().decode('utf-8')
                response_body = json.loads(response_body)
                if 'addresses' in response_body:
                    try:
                        latitude = response_body['addresses'][0]['y']
                        longitude = response_body['addresses'][0]['x']
                        print('Success!')
                    except IndexError as ie:
                        print('error!')
                        latitude = None
                        longitude = None
                else:
                    print("'result' not exist!")
                    latitude = None
                    longitude = None
            else:
                print('Response error code %d' % rescode)
                latitude = None
                longitude = None
        
        print("주소 : {0}, 위경도 : {1},{2}".format(row['소재지지번주소'],latitude,longitude))
        # geo_coordi.append([latitude, longitude])

    # np_geo_coordi = np.array(geo_coordi)
    # pd_geo_coordi = pd.DataFrame({"address":addresses['소재지지번주소'],
    #                               "latitude":np_geo_coordi[:,0],
    #                               "longitude":np_geo_coordi[:,1]})

    # result = addresses.merge(pd_geo_coordi, how='left', right_on='address', left_on='소재지지번주소')
    # return pd_geo_coordi
    apart_data.iloc[idx,10] = latitude
    apart_data.iloc[idx, 11] = longitude

    return apart_data

find_position(null_data).to_csv('data/전처리 파일/부평구 아파트 위치(위경도 포함).csv', index = False)