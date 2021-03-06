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
bitrix_key = os.getenv('BITRIX_KEY')


@logger.catch
def add_to_crm(category, reason, phone, brand, serial, name, date, time):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.add.json?'
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
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.timeline.comment.add.json?'
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
        MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.list.json?'
        fields = {'filter[CATEGORY_ID]': 0,
                  'filter[CONTACT_ID]': id}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        ids = []
        logger.info(x.json())
        if 'result' in x.json():
            for item in x.json()['result']:
                ids.append(item['ID'])
        logger.info(ids)
        return ids
    return []


@logger.catch
def find_contact_by_phone():
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.contact.list.json?'
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
        # logger.info(x.json())
        # logger.info(x.text)
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
def find_deal_by_phone_direct(phone):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.contact.list.json?'
    fields = {'filter[UF_CRM_1626337817376]': phone}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    logger.info(x.json())
    try:
        id = x.json()['result'][0]['ID']
    except:
        id = None
    logger.info(id)
    return id


@logger.catch
def find_deal_by_title(title):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.list.json?'
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
    logger.info(ids)
    return ids


@logger.catch
def get_deal_by_id(id):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    # print(x.json())
    if 'result' in x.json():
        # result = x.json()['result']['UF_CRM_MPI__PAYMENT_STATE']
        rozetka_payment = x.json()['result']['UF_CRM_1625577766232']
        evopay_payment = x.json()['result']['UF_CRM_1625575668560']
        generation_payment = x.json()['result']['UF_CRM_1632743846']
        liqpay_payment = x.json()['result']['UF_CRM_1608105758266']
        # print(f'{rozetka_payment}\n'
        #       f'{evopay_payment}\n'
        #       f'{generation_payment}\n'
        #       f'{liqpay_payment}')
        if (rozetka_payment is not None
            or evopay_payment is not None
            or generation_payment is not None
                or liqpay_payment is not None):
            return True
    return False


@logger.catch
def get_link_by_id(id):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['UF_CRM_DEAL_LIQPAY']
    return result


@logger.catch
def check_open_deals(deals):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
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
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
    PRODUCT_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.productrows.get.json?'
    DEAL_STATUSES = ['ON_HOLD', 'WON', 'LOSE']
    result = []
    for id in deals.split(','):
        fields = {'id': id}
        url = MAIN_URL + urlencode(fields, doseq=True)
        x = requests.get(url)
        if 'result' in x.json():
            stage = x.json()['result']['STAGE_ID']
            if stage not in DEAL_STATUSES:
                fields = {'id': id}
                url = PRODUCT_URL + urlencode(fields, doseq=True)
                x = requests.get(url)
                # print(x.json())
                # item = x.json()['result']['UF_CRM_ROW_FIELD'].replace('\n', '')
                title = x.json()['result'][0]['PRODUCT_NAME']
                # name = f'{title} ({item[2:]})'
                result.append([title, id])
                logger.info(title)
    return result


@logger.catch
def get_product_info(deal):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
    fields = {'id': deal}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    if 'result' in x.json():
        item = x.json()['result']['UF_CRM_ROW_FIELD']
        item = item.replace('\n', '')
        logger.info(item)
        return item[2:]
    return None


@logger.catch
def get_deal_product(id):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['UF_CRM_1623160178062']
    return result


@logger.catch
def get_link_product(id):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['UF_CRM_1609944485620']
    return result


@logger.catch
def get_contact_name(id):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.contact.get.json?'
    fields = {'id': id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    result = ''
    if 'result' in x.json():
        result = x.json()['result']['NAME']
    return result


@logger.catch
def key_fields_check(id, products):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
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
        for item in products:
            defined_key = [key1, key2, key3, key4][products.index(item)]
            result.append([defined_key, item])
        return result
    return result


@logger.catch
def send_model_field(deal_id, item_name, category, price, link):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.update.json?'
    fields = {'id': deal_id,
              'fields[UF_CRM_1623160178062]': item_name,
              'fields[UF_CRM_1626684024072]': category,
              'fields[UF_CRM_1623160196990]': price,
              'fields[UF_CRM_1609944485620]': link}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    logger.info(x.json())


@logger.catch
def get_username(deal_id):
    MAIN_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.deal.get.json?'
    SECONDARY_URL = f'https://supportua.bitrix24.ua/rest/2067/{bitrix_key}/crm.contact.get.json?'
    fields = {'id': deal_id}
    url = MAIN_URL + urlencode(fields, doseq=True)
    x = requests.get(url)
    contact_id = x.json()['result']['CONTACT_ID']
    fields = {'id': contact_id}
    url = SECONDARY_URL + urlencode(fields, doseq=True)
    y = requests.get(url)
    result = 'Користувач'
    logger.info(y.json())
    if 'result' in x.json():
        result = y.json()['result']['NAME'] + ' ' + \
                        y.json()['result']['LAST_NAME']
    return result


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
    id = find_deal_by_phone_direct('0938049900')
    print(id)
    deals = find_deal_by_contact(id)
    print(deals)

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
