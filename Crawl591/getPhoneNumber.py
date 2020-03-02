import json
from bs4 import BeautifulSoup
import requests
import re
from lxml import html
from requests.exceptions import ConnectionError
from pyvirtualdisplay import Display

import os 
import pandas as pd
import time
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}

def getPhoneData(personURL):
    try:
        session = requests.Session()
        res = session.get(personURL, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        if(soup.find('span', id="phone-num")):
            return soup.find('span', id="phone-num").text
        else:
            return personURL
    except ConnectionError:
        return personURL


def trimInfoURL(urlData):
    urlData = urlData.replace('"', "")
    urlData = urlData.replace('\\', "")
    return urlData
def handleOneCity(area, cityInfo):
    fileName = "./%s/%s" %(area, cityInfo['txt']+'.txt')
    if(not os.path.exists("./%s_電話號碼/%s" %(area, cityInfo['txt']+'.xlsx'))):
        print("    Crawling city : %s" %(cityInfo['txt']))
        with open(fileName) as city:
            phoneNumList = []
            dataInfo = {}
            start = time.time()
            ctr = 0
            for url in city.readlines():
                if(url == "\n"):
                    break
                personURL = trimInfoURL(url)
                phoneNumList.append(getPhoneData(personURL))
                ctr = ctr+1
            end = time.time()
            df1 = pd.DataFrame(data=phoneNumList, columns=['電話號碼'])
            df2 = pd.DataFrame(data=[ctr], columns=['數量'])
            df3 = pd.DataFrame(data=["%.2f 秒" %(end-start)], columns=['爬蟲耗時'])
            finalDF = pd.concat([df1, df2, df3], axis=1)
            finalDF = finalDF.fillna("")
            finalDF.to_excel("./%s_電話號碼/%s" %(area, cityInfo['txt']+'.xlsx'))

# 21440
def main():
    print("... Start crawling ...")
    with open('TaiwanCitiesInfo.json') as json_file:  
        Cities = json.load(json_file)
    # for area in Cities:
    area = "南部"
    print("[ %s ]"%(area))
    if(not os.path.exists('%s_電話號碼' %(area))):
        os.mkdir('%s_電話號碼' %(area))
    for cityInfo in Cities[area]:
        handleOneCity(area, cityInfo)
main() 

# session = requests.Session()
# res = session.get("https://www.591.com.tw/broker25465", allow_redirects=True)
# phoneNum = soup.find_all('span', id='phone-num')


