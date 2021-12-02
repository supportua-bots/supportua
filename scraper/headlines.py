import os
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


DRIVER_PATH = os.path.join(os.path.dirname(__file__), 'chromedriver')

SEARCH_XPATH = '/html/body/app-root/div/div/rz-header/header/div/div/div/form/div/div/input'
SEARCH_BUTTON = '/html/body/app-root/div/div/rz-header/header/div/div/div/form/button'


def get_product_page(code):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    # driver=webdriver.Chrome(executable_path='/usr/local/bin/chromedriver',options=options)
    driver.get('https://rozetka.com.ua/')
    driver.find_element_by_xpath(SEARCH_XPATH).send_keys(code)
    time.sleep(0.5)
    driver.find_element_by_xpath(SEARCH_BUTTON).click()
    get_url = driver.current_url
    title = get_product_title(get_url)
    return title


def get_product_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find('h1', class_='product__title').get_text()
    return title


def get_product_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find('h1', class_='product__title').get_text()
    # pps = soup.find_all('div', class_='product-about__right')
    # for p in pps:
    #     print(p)

    # print(price)
    # try:
    #     price = soup.find('p', class_='product-prices__big').get_text()
    # except:
    #     price = '0'
    category_path = ''
    categories = soup.find_all(
        'li', class_='breadcrumbs__item ng-star-inserted')
    for item in categories:
        result = item.find('span').get_text()
        category_path += result + ', '
    category_path = category_path[:-2]
    return [title, category_path]


if __name__ == "__main__":
    get_product_page(273120533)
