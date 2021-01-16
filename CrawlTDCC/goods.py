from bs4 import BeautifulSoup
import requests
import re
# from lxml import html
import chardet
import json
import os
import pandas as pd


# '元大證券股份有限公司', '台灣摩根士丹利證券股份有限公司', '西班牙商西班牙對外銀行股份有限公司臺北分公司', '法商東方匯理銀行台北分行', '法商法國巴黎銀行股份有限公司台北分公司', 
# '法商法國外貿銀行台北分行', '法商法國興業銀行台北分行', '花旗環球證券股份有限公司', '美商高盛亞洲證券有限公司台北分公司', '美商摩根大通銀行台北分行', '英商巴克萊銀行股份有限公司台北分行', '英商渣打銀行股份有限公司台北分公司', '香港商香港上海匯豐銀行股份有限公司台北分公司', '香港商野村國際證券有限公司台北分公司', '香港商蘇皇證券亞洲有限公司台北分公司', '荷商安智銀行台北分行', '新加坡商星展銀行股份有限公司台北分行', '瑞士商瑞士信貸銀行股份有限公司台北分行', '瑞士商瑞士信貸銀行股份有限公司台北證券分公司', '瑞士商瑞士銀行台北分行', '德商德意志銀行股份有限公司台北分公司', '澳商澳盛銀行集團股份有限公司台北分公司'
agent_table = ["A9800000", "A1470000", "A3260000", "A0860000", "A0820000", "A3280000", "A0370000", "A1590000", "A1480000", "A0760000", "A3220000", "A0830000", 
                "A3250000", "A1560000", "A1400000", "A0930000", "A0780000", "A3230000", "A1520000", "A0920000", "A0720000", "A0390000"]



##### Ex: 摩根士丹利, 從 2016 開始算 5 年
agent_code = ["A1470000"]
base_year = 2011
year_counter = 10
output_name = "result_goods_morgan.csv"

##### Ex: 全部, 從 2016 開始算 5 年

##############
# agent_code = ["A9800000", "A1470000", "A3260000", "A0860000", "A0820000", "A3280000", "A0370000", "A1590000", "A1480000", "A0760000", "A3220000", "A0830000", 
#                 "A3250000", "A1560000", "A1400000", "A0930000", "A0780000", "A3230000", "A1520000", "A0920000", "A0720000", "A0390000"]
# base_year = 2020
# year_counter = 1
# output_name = "result_goods.csv"
##############

def get_raw_data(agent_code, page, y):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36", "Content-Type": "application/x-www-form-urlencoded"}
    baseURl = "https://structurednotes-announce.tdcc.com.tw/Snoteanc/apps/bas/BAS210.jsp"
    session = requests.Session()
    form_data = {}
    form_data["AGENT_CODE"] = agent_code
    form_data["ISSUE_ORG_UUID"] = ""
    form_data["SALE_ORG_UUID"] = ""
    form_data["FUND_LINK_TYPE"] = "1"
    form_data["FUND_CURR"] = ""
    form_data["stopDateStart"] = ""
    form_data["stopDateEnd"] = ""
    form_data["agentDateStart"] = ("%s/1/1" %(y))
    form_data["agentDateEnd"] = ("%s/12/31" %(y))
    form_data["action"] = "Q"
    form_data["LAST_ORDER_BY"] = "FUND_NAME"
    form_data["ORDER_BY"] = ""
    form_data["IS_ASC"] = "1"
    form_data["currentPage"] = page
    res = session.post(baseURl, headers=headers, data=form_data)
    soup = BeautifulSoup(res.text, "lxml")
    return soup

def get_agent_name():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36", "Content-Type": "application/x-www-form-urlencoded"}
    baseURl = "https://structurednotes-announce.tdcc.com.tw/Snoteanc/apps/bas/BAS210.jsp"
    session = requests.Session()
    res = session.post(baseURl, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    code = soup.find('select', {"name":"AGENT_CODE"})
    agent_name = code.text.split("\n")
    return agent_name


def main():
    result = []
    output_agent_name = []
    print("... Start Crawling Goods Info ...\n")
    agent_name = get_agent_name()
    agent_name = agent_name[2:len(agent_name)-1]
    for idx, c in enumerate(agent_code):
        value = []
        pos = agent_table.index(c)
        output_agent_name.append(agent_name[pos])
        value.append(agent_name[pos])
        print("==== %s ====" %(agent_name[pos]))
        print("< tasks (total agents) > (%d / %d)\n" %(idx, len(agent_code)))

        for y in range(year_counter):
            print("[ year ]: %s" %(str(y+base_year)))
            idx_ctr = 0
            page_idx = 1
            continue_flag = True
            while continue_flag:
                print(" page: %d" %(page_idx))
                body = get_raw_data(c, page_idx, str(y+base_year))
                tables = body.find_all('table')
                current_page_ctr = 0
                for T in tables:
                    t = T.find_all('table')
                    ctr = 0
                    for data in t:
                        ctr_2 = 0
                        if ctr == 1:
                            tds = data.find_all('td', {"align":"left"})
                            for d in tds:
                                if (ctr_2 % 6) == 0:
                                    current_page_ctr += 1
                                    idx_ctr += 1
                                ctr_2 += 1
                        ctr += 1
                if current_page_ctr == 0:
                    continue_flag = False
                if page_idx == 1 and idx_ctr < 50:
                    continue_flag = False
                page_idx += 1
            print(" count: %d\n" %(idx_ctr))
            value.append(idx_ctr)
        result.append(value)
    df = pd.DataFrame(result)
    df = df.T
    df.to_csv(output_name, index=False, encoding="utf_8_sig")
main()