from bs4 import BeautifulSoup
import requests
import re
import math
# from lxml import html
import chardet
import json
import os
import pandas as pd

year_title = ['2016', '2017', '2018', '2019', '2020']
month_title = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

###########
base_year = 2011
year_counter = 10
###########

def get_raw_data(year, month):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36", "Content-Type": "application/x-www-form-urlencoded"}
    baseURl = "https://structurednotes-announce.tdcc.com.tw/Snoteanc/apps/rep/REP210.jsp"
    session = requests.Session()
    
    form_data = {}
    form_data["QUERY_YEAR"] = year
    form_data["QUERY_MONTH"] = month
    form_data["action"] = "Q"

    res = session.post(baseURl, headers=headers, data=form_data)
    soup = BeautifulSoup(res.text, "lxml")
    return soup

def main():
    result = []
    print("... Start Crawling Market Info ...\n")

    for y in range(base_year, base_year+year_counter):
        print("===== year: %d =====" %(y))

        for m in range(0, 12):
            m_result = []
            print("month: %d" %(m+1))
            body = get_raw_data(str(y), str(month_title[m]))
            trs = body.find_all('tr')
            for t in trs:
                row = t.find_all('tr')
                for r in row:
                    tds = r.find_all('td', {"align":"right"})
                    if len(tds) == 5:
                        m_result.append(round(float(tds[-1].text)))
            result.append(m_result)
        result.append([])

    df = pd.DataFrame(result)
    df.to_csv("market_result.csv", index=False, encoding="utf_8_sig")
main()