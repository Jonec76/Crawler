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
urlFileName = "members.txt"
membersFileName = "公會會員詳細資訊.xlsx"
baseURl = "https://www.roccpa.org.tw/member_search/"
COLUMNS = ['會計師姓名', '事務所名稱', '事務所地址', '事務所電話', '事務所傳真', 'E-mail']


def bs4Init(personURL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    session = requests.Session()
    res = session.get(baseURl+personURL, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    return soup


def getOnePersonAllDetails(soup):
    detail = soup.find('ol', class_="event-point")
    ctr = 0
    aPerson = {}
    stop = False
    for d in detail.find_all('li'):
        if(not stop):
            feature = d.text
            aPerson[d.find('b').text] = [d.find('div').text]
        if(d.find('b').text == 'E-mail'):
            stop = True
    tmpDf = pd.DataFrame(data=aPerson)
    return tmpDf


def main():
    print("... Start crawling personal informations ...\n")
    totalPersonDF = pd.DataFrame(columns=COLUMNS)
    datas = []
    data = open(urlFileName, "r")
    datas = data.readlines()
    start = time.time()
    print(" [1] Total person numbers: %d" % (len(datas)))
    ctr=0
    for person in datas:
        soup = bs4Init(person)
        aPersonDF = getOnePersonAllDetails(soup)
        totalPersonDF = totalPersonDF.append(aPersonDF, ignore_index=True)
        if(ctr%100 == 0):
            print("     第 %d 人" %(ctr))
        ctr = ctr + 1
    totalPersonDF = totalPersonDF.fillna("")
    totalPersonDF = totalPersonDF[COLUMNS]
    totalPersonDF.to_excel(membersFileName)
    end = time.time()
    print(" [2] Time take: %.2f" % (end-start))
    print("\n... End crawling personal informations ...")



main()
