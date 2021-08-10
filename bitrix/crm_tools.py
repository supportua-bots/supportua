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


@logger.catch
def add_to_crm(category, reason, phone, brand, serial, name, date, time):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/cml51zgfaxwxwa2x/crm.deal.add.json?'
    fields = {'fields[CATEGORY_ID]': 11,
              'fields[STAGE]': 'Нове звернення',
              'fields[UF_CRM_1620715237492]': category,
              'fields[UF_CRM_1612445730392]': phone,
              'fields[UF_CRM_1612436268887]': brand,
              'fields[UF_CRM_1612436246623]': serial,
              'fields[UF_CRM_1620715280976]': reason,
              'fields[UF_CRM_1620726993270]': name,
              'fields[UF_CRM_1620715319172]': date,
              'fields[UF_CRM_1620715309625]': time,
              'fields[ASSIGNED_BY_ID]': OWNER_ID}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    return x.json()['result']


@logger.catch
def add_comment(deal_id, comment):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/96pk71aujg4fj1r7/crm.timeline.comment.add.json?'
    fields = {'fields[ENTITY_ID]': deal_id,
              'fields[ENTITY_TYPE]': 'deal',
              'fields[COMMENT]': comment}
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


@logger.catch
def find_deal_by_contact(id):
    if id is not None:
        MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/4g3l60we6z7cltoj/crm.deal.list.json?'
        fields = {'filter[CATEGORY_ID]': 0,
                  'filter[CONTACT_ID]': id}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        ids = []
        logger.info(x.json())
        if 'result' in x.json():
            for item in x.json()['result']:
                ids.append(item['ID'])
        return ids
    return []


@logger.catch
def find_contact_by_phone():
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/dubn2ikjcpwxsh79/crm.contact.list.json?'
    next = 0
    result = []
    while next != 123456789:
        fields = {'select[]': 'ID',
                  'select[]': 'PHONE',
                  'start': next}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        if 'next' in x.json():
            next = int(x.json()['next'])
        else:
            next = 123456789
        if 'result' in x.json():
            for item in x.json()['result']:
                if 'PHONE' in item:
                    cleaned_phone = item['PHONE'][0]['VALUE'].replace(
                        '-', '').replace('+', '').replace(' ', '')
                    if cleaned_phone[0] == '0':
                        cleaned_phone = '38' + cleaned_phone
                    result.append([cleaned_phone, item['ID']])
    return result


@logger.catch
def find_deal_by_title(title):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/4g3l60we6z7cltoj/crm.deal.list.json?'
    fields = {'filter[CATEGORY_ID]': 0,
              'filter[TITLE]': title}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    ids = []
    try:
        for item in x.json()['result']:
            ids.append(item['ID'])
    except:
        pass
    return ids


@logger.catch
def get_deal_by_id(id):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['UF_CRM_MPI__PAYMENT_STATE']
    return result


@logger.catch
def get_link_by_id(id):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['UF_CRM_DEAL_LIQPAY']
    return result


@logger.catch
def check_open_deals(deals):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    DEAL_STATUSES = ['ON_HOLD', 'WON', 'LOSE']
    for id in deals.split(','):
        fields = {'id': id}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        if 'result' in x.json():
            result = x.json()['result']['STAGE_ID']
            if result not in DEAL_STATUSES:
                logger.info(id)
                logger.info(result)
                return id
    return None


@logger.catch
def get_open_products(deals):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    result = []
    for id in deals.split(','):
        fields = {'id': id}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        if 'result' in x.json():
            item = x.json()['result']['UF_CRM_ROW_FIELD']
            title = x.json()['result']['TITLE']
            name = f'{title} ({item[2:]})'
            result.append([name, id])
            logger.info(item)
    return result


@logger.catch
def get_deal_product(id):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['UF_CRM_1623160178062']
    return result


@logger.catch
def get_link_product(id):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['UF_CRM_1609944485620']
    return result


@logger.catch
def key_fields_check(id):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/1syhxe0qhy432py0/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = []
    if 'result' in x.json():
        key1 = x.json()['result']['UF_CRM_1609749756869']
        key2 = x.json()['result']['UF_CRM_1624356024571']
        key3 = x.json()['result']['UF_CRM_1624356169034']
        key4 = x.json()['result']['UF_CRM_1624356185921']
        logger.info([key1, key2, key3, key4])
        for item in [key1, key2, key3, key4]:
            if item == '':
                return []
            else:
                result.append(item)
        return result
    return result


@logger.catch
def send_model_field(deal_id, item_name, category, link):
    MAIN_URL = 'https://supportua.bitrix24.ua/rest/2067/zgbq9h1f38vnszm2/crm.deal.update.json?'
    fields = {'id': deal_id,
              'fields[UF_CRM_1623160178062]': item_name,
              'fields[UF_CRM_1626684024072]': category,
              'fields[UF_CRM_1609944485620]': link}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    logger.info(x.json())


@logger.catch
def send_to_erp(tracking_data, chat_id):
    MAIN_URL = 'https://demoerp.support.ua/api/v1/appeal/manage'
    header = {
        'Authorization': 'Bearer $2y$10$6qgC45p616zB2zllWaiTs.fFE2syQkThx8qFOcyx1TxjO/M4LNmra'}
    datapoints = ['NAME', 'PHONE', 'CITY',
                  'BRAND', 'SERIAL', 'CONDITION', 'DETAIL']
    for datapoint in datapoints:
        if datapoint not in tracking_data:
            if datapoint == 'PHONE':
                tracking_data[datapoint] = 1234567890
            else:
                tracking_data[datapoint] = ''
        else:
            if datapoint == 'PHONE':
                try:
                    tracking_data[datapoint] = int(tracking_data[datapoint])
                except:
                    tracking_data[datapoint] = 1234567890
    names = tracking_data['NAME'].split(' ')
    if len(names) == 3:
        first = names[1]
        last = names[0]
        middle = names[2]
    elif len(names) == 2:
        first = names[1]
        last = names[0]
        middle = ''
    else:
        first = names[0]
        last = ''
        middle = ''
    fields = {
                'source': 'viber_mp_bot',
                'first_name': first,
                'second_name': middle,
                'last_name': last,
                'phone': tracking_data['PHONE'],
                'city_name': tracking_data['CITY'],
                'brand_name': tracking_data['BRAND'],
                'model_name': '',
                'serial': tracking_data['SERIAL'],
                'condition': tracking_data['CONDITION'],
                'detail': tracking_data['DETAIL'],
                }
    files = {}
    items = ['warranty', 'receipt']
    for item in items:
        try:
            file = open(f'media/{chat_id}/{item}.jpg', 'rb')
            files[item] = (f'{item}.jpg', file)
        except Exception as e:
            print(e)
    x = requests.post(MAIN_URL, data=fields, headers=header, files=files)
    logger.info(x.headers)
    logger.info(x.text)


def test():
    deals = ['22551', '24893', '22739']
    for deal in deals:
        key_fields_check(deal)


if __name__ == '__main__':
    deals = ['22551', '24893', '22739']
    for deal in deals:
        key_fields_check(deal)
    # check_open_deals(deals)
    # send_model_field('21085', 'Test name', 'Test category')
    # chat_id = '+XS2XxGhTunlRnOPpEl2NQ=='
    # tracking_data = {'PHONE': 1111111111}
    # send_to_erp(tracking_data, chat_id)
    # get_deal_by_id('21525')
    # deals_id = find_contact_by_phone('380982676660')
    # logger.info(deals_id)
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
#         logger.info(url)
#         x = requests.post(MAIN_URL, headers=header, json=url)
#         logger.info(x.json())
