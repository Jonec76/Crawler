from bs4 import BeautifulSoup
import requests
import re
from lxml import html
import chardet
import json
import os


# If totalRows - firstRow < 15, then it would still try to crawl 15 datas as much as possible



def getTotalRows(GetRowsURl):
    session = requests.Session()
    res = session.get(GetRowsURl, allow_redirects=False)
    soup = BeautifulSoup(res.text, "lxml").find('p').text
    totalRows = json.loads(soup)
    return totalRows["total"]
def getCityMemberList(region, firstRow, totalRows):
    memberList = []
    while(firstRow < totalRows):
        baseURl = "https://rent.591.com.tw/index.php?module=shop&action=rsList&region=%d&firstRow=%d&totalRows=%d" %(region, firstRow, totalRows)
        session = requests.Session()
        res = session.get(baseURl, allow_redirects=False)
        soup = BeautifulSoup(res.text, "lxml")
        members = soup.find('p').find('a').find_all('a', class_='\\"go-shop\\"')
        for m in members:
            memberList.append(m["href"])
        firstRow = firstRow + 15
    return memberList


def crawlOneCity(area, regionId, regionName):
    memberList = []
    firstRow=0
    GetRowsURl = "https://rent.591.com.tw/index.php?module=shop&action=rsList&region=%d" %(regionId) 
    totalRows = getTotalRows(GetRowsURl)
    print('    Crawling city %s,  Members: %s' %(regionName, totalRows))
    memberList = getCityMemberList(regionId, firstRow, int(totalRows))
    with open("./%s/%s.txt" %(area, regionName), 'w+') as f:
        for d in memberList:
            f.write("%s\n" % d)
        f.write('\nTotal members: %s\n' %(totalRows))
        

# main()
def main():
    print("... Start Crawling Personal Web Info ...")
    with open('TaiwanCitiesInfo.json') as json_file:  
        Cities = json.load(json_file)
    for area in Cities:
        if(not os.path.exists('%s' %(area))):
            os.mkdir('%s' %(area))
        print('\n- [ %s ]' %(area))
        for cityInfo in Cities[area]:
            crawlOneCity(area, cityInfo['id'], cityInfo['txt'])


'''
    Find the bug that the page 85 in area Kaoshiung is empty, but the total number calculates this empty page as 15 people

    # baseURl = "https://rent.591.com.tw/index.php?module=shop&action=rsList&region=%d&firstRow=%d&totalRows=%d" %(17, 1260, 2218)
    # session = requests.Session()
    # res = session.get(baseURl, allow_redirects=False)
    # soup = BeautifulSoup(res.text, "lxml")
    # print(soup)
'''




# members = soup.find('p').find('a').find_all('a', class_='\\"go-shop\\"')
# print(len(members))
# for m in members:
#     memberList.append(m["href"])
# main()
# crawlOneCity('南部', 17, '高雄市')
# officialWeb = "https://rent.591.com.tw/rentBroker.html#list"
# session = requests.Session()
# r = session.get(officialWeb, allow_redirects=False)
# soup = BeautifulSoup(r.text, "lxml")
# print(soup.find('div', id="areaBoxNew"))
# with open('official.html', 'w+') as f:
#     for d in soup:
#         f.write("%s\n" % d)

