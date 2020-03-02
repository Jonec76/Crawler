from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from lxml import html
from pprint import pprint
import json
import re
import time
import pandas as pd

DEPTS = ['listdpt', 'list']
YEARS = ['108', '107', '106', '105', '104', '103', '-1']
VALID_TITLES = ['發票號碼', '付款方式', '傳票號碼', '匯款編號']
COLUMNS = ['報帳條碼', '經費或計畫名稱', '主計室電腦代號', '計畫費用別', '購案編號', '發票號碼', '用途及摘要', '金     額(單據清單)', '小  計(單據清單)', '付款方式', '受款人基本資料', '金     額(付 款 方 式)',
           '備註', '小  計(付 款 方 式)', '傳票號碼', '傳票日期', '摘要(傳 票 資 料)', '會計UID', '匯款編號', '作業日期', '匯出日期', '摘要(付 款 資 料)', '統一編號', '銀行代號', '銀行帳號', '出納UID']
getDBLinkNum = re.compile(r'\d+')
tableData = []


def getTotalPageNum(driver, dept, year):
    driver.get(
        'https://ntuacc.cc.ntu.edu.tw/acc/apply/%s.asp?yearchoose=%s&Page=1' % (dept, year))
    x = driver.find_element_by_xpath(
        '//*[@id="AutoNumber2"]/tbody/tr/td[2]/div/font')
    lastPage = x.text.split('/')[-1]
    return int(lastPage)


def alignDatas(rowData):
    maxNumTR = 0
    for r in rowData:
        if(len(r) > maxNumTR):
            maxNumTR = len(r)
    for r in rowData:
        for i in range(len(r), maxNumTR):
            r.append("")
    return rowData


def getStartIdx(tableIdx):
    if(tableIdx == 0):
        return 5
    elif(tableIdx == 1):
        return 9
    elif(tableIdx == 2):
        return 14
    else:
        return 18


def getSumIdx(tableIdx):
    if(tableIdx == 0):
        return 8
    else:
        return 13


def HasSumRow(table):
    if(table == 0 or table == 1):
        return True
    else:
        return False


def checkValidTable(tableIdx, title):
    if(title == VALID_TITLES[tableIdx]):
        return True
    return False


def getDBLinkData(rowData, doubleClickURL, driver):
    res = driver.get(doubleClickURL)
    soup = BeautifulSoup(driver.page_source, "lxml")
    header = soup.find('center').find('table')
    datas = {}
    colums = []
    tableIdx = 0
    headerIdx = 1
    for td in header.findAll('td'):
        start = False
        firstToThird = ""
        for c in td.text:
            if(start):
                firstToThird = firstToThird + c
            if(c == "："):
                start = True
        rowData[headerIdx].append(firstToThird)
        headerIdx = headerIdx + 1
    soup = soup.find('center').find('center').findAll('table')

    for s in soup[0:-1]:
        if (checkValidTable(tableIdx, s.find('td').text)):
            rows = s.findAll('tr')
            if(HasSumRow(tableIdx)):
                for row in rows[0:-1]:
                    if(row.has_attr('bgcolor')):
                        continue
                    else:
                        startIdx = getStartIdx(tableIdx)
                        for elem in row.findAll('td'):
                            if(elem.text != '　'):
                                rowData[startIdx].append(elem.text)
                                startIdx = startIdx + 1
                sumIdx = getSumIdx(tableIdx)
                rowData[sumIdx].append(rows[-1].findAll('td')[1].text)
            else:
                for row in rows:
                    if(row.has_attr('bgcolor')):
                        continue
                    else:
                        startIdx = getStartIdx(tableIdx)
                        for elem in row.findAll('td'):
                            rowData[startIdx].append(elem.text)
                            startIdx = startIdx + 1
            tableIdx = tableIdx + 1
    return rowData


def getPage(driver, pageURL, doubleClickBaseURL, tableData):
    res = driver.get(pageURL)
    soup = BeautifulSoup(driver.page_source, "lxml")
    soupLink = soup.find('form', {"name": "forms"}).findAll(
        'tbody')[-1].findAll('tr')
    for sl in soupLink:
        if(sl.has_attr('ondblclick')):
            tableData[0].append(sl.find('td').text)
            doubleClickURL = doubleClickBaseURL + \
                getDBLinkNum.findall(sl['ondblclick'])[0]
            tableData = getDBLinkData(tableData, doubleClickURL, driver)
            tableData = alignDatas(tableData)


def initDriver():
    with open('config.json') as json_file:
        config = json.load(json_file)
    account = config["account"]
    password = config["password"]
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # hide the driver
    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.get('https://ntuacc.cc.ntu.edu.tw/acc/index.asp?campno=m&idtype=5')
    driver.find_element_by_xpath('//*[@id="id"]').send_keys(account)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    driver.find_element_by_xpath('//*[@id="vsub"]/td/input').click()
    return driver


def initTableData():
    tableData = []
    for i in range(len(COLUMNS)):
        tableData.append([])
    return tableData


def getDeptName(dept):
    if(dept == 'listdpt'):
        return "報帳管理"
    elif(dept == "list"):
        return "計畫經費"


def outputFile(tableData, dept, year):
    output = {}
    for i in range(len(COLUMNS)):
        output[COLUMNS[i]] = tableData[i]
    df2 = pd.DataFrame(data=output)
    df2.to_excel("%s_%s.xlsx" % (year, dept))


def renderAccount(dept, year):
    driver = initDriver()
    totalPageNum = getTotalPageNum(driver, dept, year)
    for n in range(totalPageNum):
        CURRENT_PAGE = str(n+1)
        pageURL = 'https://ntuacc.cc.ntu.edu.tw/acc/apply/%s.asp?yearchoose=%s&Page=%s' % (
            dept, year, CURRENT_PAGE)
        doubleClickBaseURL = "https://ntuacc.cc.ntu.edu.tw/acc/apply/appshow.asp?yearchoose=%s&page=%s&bugetno=&sn=" % (
            year, CURRENT_PAGE)
        getPage(driver, pageURL, doubleClickBaseURL, tableData)
    # outputFile(tableData, dept, year)


tableData = initTableData()
for dept in DEPTS:
    renderAccount(dept, YEARS[0])
outputFile(tableData, '報帳管理', YEARS[0])
