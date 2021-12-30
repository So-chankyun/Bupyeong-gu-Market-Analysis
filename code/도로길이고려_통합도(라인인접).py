#!/usr/bin/env python
# coding: utf-8
'''
기초구역 경계에 인접한 도로의 정보와 그렇지 않은 도로의 정보를
결합하는 코드이다.
'''

import pandas as pd
import missingno as msno
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import geopandas as gpd

font_path = r'C:/Users/user/NanumFontSetup_TTF_ALL/NanumGothic.ttf'
font_name = font_manager.FontProperties(fname=font_path, size=18).get_name()
rc('font',family=font_name)

# 데이터 로드
path = r'C:/Data Analysis/부평구 상권분석/data/전처리 파일/부평구 도로_5181/3. 기초구역별 도로통합도/기초구역별 통합도 집계 전/start/'
not_near_line = gpd.read_file(path+'기초구역별_도로통합도_라인미인접/기초구역별_도로통합도_라인미인접_st_5181.shp',encoding='euc-kr')
near_line = gpd.read_file(path+'기초구역별_도로통합도_라인인접/기초구역별_도로통합도_라인인접_st_5181.shp',encoding='euc-kr')

# 필요한 컬럼 명세
essential_col = ['BAS_AR','BAS_ID','Ref','x1','y1','x2','y2','Con','IntHH','IntHH_R2','IntHH_R3','IntHH_R5',
                 'IntTekl','IntTekl_R2','IntTekl_R3','IntTekl_R5','Line Lengt','geometry']

# 필요 데이터 추출
nnl_data = not_near_line[essential_col] # not near line
nl_data = near_line[essential_col] # near line

# 컬럼명 변경
nnl_data = nnl_data.rename(columns={'Line Lengt':'LL'})
nl_data = nl_data.rename(columns={'Line Lengt':'LL'})

# 새로운 컬럼 생성
new_col = ['IntHH_RI','IntHH_R2_RI','IntHH_R3_RI','IntHH_R5_RI','IntTekl_RI','IntTekl_R2_RI'
            ,'IntTekl_R3_RI','IntTekl_R5_RI']
use_col = ['IntHH','IntHH_R2','IntHH_R3','IntHH_R5','IntTekl','IntTekl_R2','IntTekl_R3','IntTekl_R5']

df_list = [nnl_data,nl_data]

for i in range(len(df_list)):
    for idx in range(len(new_col)):
        df_list[i][new_col[idx]] = df_list[i][use_col[idx]]*df_list[i]['LL']

# Integration column list 생성
Int_list = nnl_data.columns[18:]

# 두 Dataframe 결합
merge_data = pd.concat([nnl_data, nl_data], ignore_index=True)

# 기초구역별 통합도 합산
sum_of_integration_by_bi = merge_data.groupby('BAS_ID')[Int_list].sum().reset_index()
avg_of_integration_by_bi = merge_data.groupby('BAS_ID')[use_col].mean().reset_index()

# 그래프 레이아웃 지정
fig, axes = plt.subplots(len(Int_list),2,figsize=(15,40),constrained_layout=True)
color = ['red','yellow','navy','green','blue','magenta','violet','skyblue']

# 그래프 생성
for idx in range(len(Int_list)):
    sns.histplot(ax=axes[idx,0],data=sum_of_integration_by_bi, x=Int_list[idx], kde=True,color=color[idx])
    sns.histplot(ax=axes[idx,1],data=avg_of_integration_by_bi, x=use_col[idx], kde=True,color=color[idx])
    axes[idx,0].set_title('CONSIDER LINE LENGTH')  
    axes[idx,1].set_title('AVERAGE OF INTEGRATION WITHIN BASIS AREA')  
    
plt.show()

# 결과 저장
path = r'C:/Data Analysis/부평구 상권분석/data/전처리 파일/부평구 도로_5181/3. 기초구역별 도로통합도/기초구역별 통합도 집계 후/start/결합전/'
sum_of_integration_by_bi.to_csv(path+'기초구역별_도로별_통합도(라인인접고려,결합전)_st_5181.csv')
avg_of_integration_by_bi.to_csv(path+'기초구역별_통합도(평균,라안인접고려,결합전)_st_5181.csv')

# 기초구역 로딩
basic_area = gpd.read_file('./data/전처리 파일/부평구_기초구역_5181/부평구_기초구역_5181.shp')

# 데이터 타입 변경
sum_of_integration_by_bi = sum_of_integration_by_bi.astype({'BAS_ID':'object'})
avg_of_integration_by_bi = avg_of_integration_by_bi.astype({'BAS_ID':'object'})

# 데이터 병합
result1 = basic_area.merge(sum_of_integration_by_bi,left_on='BAS_ID',right_on='BAS_ID',how='inner')
result2 = basic_area.merge(avg_of_integration_by_bi,left_on='BAS_ID',right_on='BAS_ID',how='inner')

result1.sort_values(by='BAS_ID',axis=0,inplace=True)
result2.sort_values(by='BAS_ID',axis=0,inplace=True)

path = r'C:/Data Analysis/부평구 상권분석/data/전처리 파일/부평구 도로_5181/3. 기초구역별 도로통합도/기초구역별 통합도 집계 후/start/결합후/'
result1.to_csv(path+'기초구역별_도로별_통합도(라인인접고려,결합후)_st_5181.csv')
result2.to_csv(path+'기초구역별_통합도(평균,라인인접고려,결합후)_st_5181.csv')