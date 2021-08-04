import requests
from bs4 import BeautifulSoup


def get_product_title(url):
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
    link = 'https://rozetka.com.ua/273120533/p273120533/'
    print(get_product_title(link))
