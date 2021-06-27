import requests
from bs4 import BeautifulSoup


def get_product_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find('h1', class_ ='product__title').get_text()
    return title


if __name__=="__main__":
    link = 'https://rozetka.com.ua/asus_90nr04d1_m04220/p263190441/'
    print(get_product_title(link))
