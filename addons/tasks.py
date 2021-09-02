import json
from db_func.database import get_all_tasks, delete_task, check_user, update_task_counter
from bitrix.crm_tools import key_fields_check, get_product_info, get_deal_product, get_contact_name
from viberbot.api.messages.text_message import TextMessage
from vibertelebot.utils.tools import keyboard_consctructor
from vibertelebot.main import viber
from textskeyboards import viberkeyboards as kb
from textskeyboards import texts as resources
from vibertelebot.handlers import operator_connection
from loguru import logger


def send_message_to_user(user, keys, username, device):
    user_info = check_user(user)
    logger.info(user_info)
    if user_info:
        phone = user_info[0][1]
        deal = user_info[0][3]
    else:
        phone = ''
        deal = ''
    logger.info(user)
    product = get_deal_product(deal)
    text = resources.found_key.replace('[name]', username).replace(
        '[products]', keys).replace('[device]', device)
    logger.info(text)
    tracking_data = {'NAME': username,
                     'HISTORY': '',
                     'CHAT_MODE': 'on',
                     'STAGE': 'menu',
                     'PHOTO_MODE': 'off',
                     'DEAL': deal,
                     'PHONE': phone}
    tracking_data = json.dumps(tracking_data)
    viber.send_messages(user, [TextMessage(text=text,
                                           keyboard=kb.operator_keyboard,
                                           tracking_data=tracking_data)])


@logger.catch
def task_checker():
    tasks = get_all_tasks()
    logger.info(tasks)
    for item in tasks:
        product = get_product_info(item[2])
        splitted_products = product.split(';')
        keys = key_fields_check(item[2], splitted_products)
        text = ''
        logger.info(f'Keys: {keys}')
        added_keys = False
        for word in keys:
            counter = keys.index(word) + 1
            logger.info(f'Counter: {counter}')
            text += f'{counter}. Сервіс {word[1]}, ваш електронний ключ:\n{word[0]}\n'
            if word[0]:
                added_keys = True
            else:
                added_keys = False
        if added_keys:
            send_message_to_user(item[0], text, username, device)
            delete_task(item[0])
        else:
            if int(item[4]) > 5:
                user_info = check_user(item[0])
                logger.info(user_info)
                if user_info:
                    username = user_info[0][4]
                    phone = user_info[0][1]
                    deal = user_info[0][3]
                else:
                    username = 'ViberUser'
                    phone = ''
                    deal = ''
                tracking_data = {'NAME': username,
                                 'HISTORY': '',
                                 'CHAT_MODE': 'on',
                                 'STAGE': 'menu',
                                 'PHOTO_MODE': 'off',
                                 'DEAL': deal,
                                 'PHONE': phone}
                delete_task(item[0])
                operator_connection(item[0], tracking_data)
            else:
                update_task_counter(item[0], int(item[4]))
