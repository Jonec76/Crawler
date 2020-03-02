from bs4 import BeautifulSoup
import requests
import re
from lxml import html
import chardet
import json
import os

fileName = "members.txt"

def bs4Init():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    baseURl = "https://www.roccpa.org.tw/member_search/list2?AntiToken=5xZ%2FUSbPaDRfbDWJRxyNkeATshO2mGQk2x5fA%2F3YfZo%3D&location=&fields=1&keys=&p=2"
    session = requests.Session()
    res = session.get(baseURl, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    return soup

def getTotalPage(soup):
    data = soup.find('span', class_='page-txt').text
    trim = False
    pageNum = ""
    for c in data:
        if c == '頁':
            trim = False
        if(trim):
            pageNum += c
        if c == '/':
            trim = True
    try:
        return int(pageNum)
    except ValueError:
        return 500


def getMemberInfo(pageNum):
    Members = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    print(" [1] Total page numbers: %d" % (pageNum))
    for i in range(pageNum):
        num = i+1
        baseURl = 'https://www.roccpa.org.tw/member_search/list2?AntiToken=5xZ%2fUSbPaDRfbDWJRxyNkeATshO2mGQk2x5fA%2f3YfZo%3d&location=&fields=1&keys=&p={0}'.format(
            num)
        session = requests.Session()
        res = session.get(baseURl, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        for info in soup.find_all('a', class_="more"):
            Members.append(info['href'])
    return Members


def main():
    print("... Start Crawling Personal Web Info ...\n")
    soup = bs4Init()
    pageNum = getTotalPage(soup)
    Members = getMemberInfo(pageNum)
    print(" [2] Write out the personal informations: %s" % (fileName))
    with open(fileName, 'w+') as f:
        for m in Members:
            f.write("%s\n" % m)
    print("\n... Finish Crawling Personal Web Info ...")

main()
