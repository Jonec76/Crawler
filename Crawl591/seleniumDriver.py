from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
from lxml import html
from pprint import pprint
import json
import re
import time


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception('Timeout waiting')


def click_through_to_new_page(browser):
    link = browser.find_element_by_class_name('pageNext')
    link.click()

    def link_has_gone_stale():
        try:
            # poll the link with an arbitrary call
            link.find_elements_by_tag_name('li')
            return False
        except StaleElementReferenceException:
            return True
    wait_for(link_has_gone_stale)


def driverInit():
    listData = []
    lastPageNum = 0
    # options: For skipping the driver notification.
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.get("https://rent.591.com.tw/rentBroker.html")
    pageBar = driver.find_element_by_class_name('pageBar')
    for r in pageBar.find_elements_by_class_name('pageNum-form'):
        lastPageNum = r.text

    for i in range(int(lastPageNum)+1):
        memberList = driver.find_element_by_id(
            'smallList').find_element_by_tag_name('ul')
        for u in memberList.find_elements_by_tag_name('li'):
            if(u.get_attribute('link')):
                listData.append(u.get_attribute('link'))
        click_through_to_new_page(driver)
    return listData


listData = driverInit()
with open('Taipei.txt', 'w') as f:
    for item in listData:
        f.write("%s\n" % item)



