import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from config import *
import pymongo
client = pymongo.MongoClient(MONGO_url)
db = client[MONGO_DB]
browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)
def search():
    try:
        browser.get('https://www.taobao.com/')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#q'))
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        input.send_keys('美食')
        submit.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutException:
        return search()
def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_number)))
        get_products()
    except TimeoutException:
        next_page(page_number)
def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    html = browser.page_source
    soup = BeautifulSoup(html,'lxml')
    items = soup.select('#mainsrp-itemlist > div > div > div > div')
    # print(items)
    for item in items:
        # print(item)
        product = {
            'price': item.select('.price')[0].get_text().strip('\n'),
            'deal': item.select('.deal-cnt')[0].get_text().strip('\n'),
            'title':item.select('.title')[0].get_text().strip('\n'),
            'shop': item.select('.shop')[0].get_text().strip('\n'),
            'location':item.select('.location')[0].get_text().strip('\n'),
        }
        print(product)
        save_to_mongo(product)
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储成功')
    except Exception:
        print('存储失败')
def main():
    try:
        total = search()
        total = int(re.findall('(\d+)',total)[0])
        # print(total)
        for i in range(2,total+1):
            next_page(i)
    finally:
        browser.close()
if __name__ == '__main__':
    main()

