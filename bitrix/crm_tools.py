import os
import base64
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime, date, timedelta
from bitrix.admin import OWNER_ID, SECTION_ID
# from admin import OWNER_ID, SECTION_ID
from loguru import logger


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

# OWNER_ID, SECTION_ID = range(2)


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def add_to_crm(category, reason, phone, brand, serial, name, date, time):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/cml51zgfaxwxwa2x/crm.deal.add.json?'
    fields = {'fields[CATEGORY_ID]':11,
              'fields[STAGE]':'Нове звернення',
              'fields[UF_CRM_1620715237492]':category,
              'fields[UF_CRM_1612445730392]':phone,
              'fields[UF_CRM_1612436268887]':brand,
              'fields[UF_CRM_1612436246623]':serial,
              'fields[UF_CRM_1620715280976]':reason,
              'fields[UF_CRM_1620726993270]':name,
              'fields[UF_CRM_1620715319172]':date,
              'fields[UF_CRM_1620715309625]':time,
              'fields[ASSIGNED_BY_ID]':OWNER_ID}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    return x.json()['result']


@logger.catch
def add_comment(deal_id, comment):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/96pk71aujg4fj1r7/crm.timeline.comment.add.json?'
    fields = {'fields[ENTITY_ID]':deal_id,
              'fields[ENTITY_TYPE]':'deal',
              'fields[COMMENT]':comment}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    return x.json()['result']


@logger.catch
def upload_image(path):
    url = "https://api.imgbb.com/1/upload"
    api_key = os.getenv('IMAGE_API')
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    params = {
        'key': api_key,
        'image': encoded_string
    }
    r = requests.post(url, data=params)
    return r.json()['data']['url']


def find_deal_by_contact(id):
    if id is not None:
        MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/4g3l60we6z7cltoj/crm.deal.list.json?'
        fields = {'filter[CATEGORY_ID]': 0,
                  'filter[CONTACT_ID]': id}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        ids = []
        try:
            for item in x.json()['result']:
                ids.append([item['ID'], item['TITLE']])
        except:
            pass
        return ids
    return []


def find_contact_by_phone(phone):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/dubn2ikjcpwxsh79/crm.contact.list.json?'
    next = 0
    while next != 1234567:
        fields = {'select[]': 'ID',
                  'select[]': 'PHONE',
                  'start': next}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        if 'next' in x.json():
            next = int(x.json()['next'])
        else:
            next = 1234567
        try:
            for item in x.json()['result']:
                # print(item['ID'])
                if 'PHONE' in item:
                    cleaned_phone = item['PHONE'][0]['VALUE'].replace('-', '').replace('+', '').replace(' ', '')
                    if cleaned_phone[0] == '0':
                        cleaned_phone = '38' + cleaned_phone
                    if phone == cleaned_phone:
                        return item['ID']
        except:
            pass
    return ''


def find_deal_by_title(title):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/4g3l60we6z7cltoj/crm.deal.list.json?'
    fields = {'filter[CATEGORY_ID]': 0,
              'filter[TITLE]': title}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    ids = []
    try:
        for item in x.json()['result']:
            ids.append([item['ID'], item['TITLE']])
    except:
        pass
    return ids


def get_deal_by_id(id):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    print(x.json()['result'])
    print(x.json()['result']['UF_CRM_DEAL_LIQPAY'])
    print(x.json()['result']['UF_CRM_MPI__PAYMENT_STATE'])


if __name__ == '__main__':
    get_deal_by_id('21525')
#     MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/qfhlg4mpu5jyz7kn/entity.item.add.json'
#     with open("photo2870.jpg", "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read())
#         header = {'Content-Type': 'text/plain'}
#         data = {'auth':'qfhlg4mpu5jyz7kn',
#                 'ENTITY': 'menu',
#                 'NAME':'testtyhing',
#                 'DETAIL_PICTURE[0]':'test.jpg',
#                 'DETAIL_PICTURE[1]':encoded_string}
#         url = urlencode(data, doseq=True)
#         print(url)
#         x = requests.post(MAIN_URL, headers=header, json=url)
#         print(x.json())
