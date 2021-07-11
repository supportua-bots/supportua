import os
import glob
import json
import jsonpickle
import time
import requests
import vibertelebot.utils.additional_keyboard as addkb
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from datetime import date, datetime, timedelta
from textskeyboards import texts as resources
from vibertelebot.utils.tools import keyboard_consctructor, save_message_to_history, workdays, divide_chunks
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.contact_message import ContactMessage
from viberbot.api.messages.location_message import LocationMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from viberbot.api.messages.picture_message import PictureMessage
from jivochat import sender as jivochat
from jivochat.utils import resources as jivosource
from bitrix.crm_tools import (find_deal_by_contact,
                            find_deal_by_title, upload_image, get_deal_by_id, get_link_by_id)
from db_func.database import check_phone, add_task, task_active
from textskeyboards import viberkeyboards as kb
from scraper.headlines import get_product_title
from loguru import logger



dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def deals_grabber(phone, chat_id, tracking_data, viber):
    contact_id = check_phone(phone)
    if contact_id:
        logger.info('Found contact_id')
        logger.info(contact_id)
        deals = find_deal_by_contact(contact_id[0][0])
        logger.info(deals)
        tracking_data['DEALS'] = deals
        if len(deals) == 0 or len(deals) > 1:
            reply_keyboard = kb.operator_keyboard
            reply_text = resources.specify_deal_id
            tracking_data['STAGE'] = 'deal'
        else:
            reply_keyboard = kb.menu_keyboard
            reply_text = resources.menu_message
            tracking_data['DEAL'] = deals[0]
    else:
        logger.info('Not found contact_id')
        reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
        reply_text = resources.phone_error
        tracking_data['STAGE'] = 'phone'
        logger.info(tracking_data)
    tracking_data = json.dumps(tracking_data)
    reply = [TextMessage(text=reply_text,
                         keyboard=reply_keyboard,
                         tracking_data=tracking_data,
                         min_api_version=3)]
    viber.send_messages(chat_id, reply)


@logger.catch
def operator_connection(chat_id, tracking_data):
    with open(f'media/{chat_id}/history.txt', 'r') as f:
        history = f.read()
    jivochat.send_message(chat_id,
                          tracking_data['NAME'],
                          history,
                          'viber')
    try:
        with open(f'media/{chat_id}/links.txt', 'r') as f:
            content = f.read()
            links = content.split(',')
            for link in links:
                link = link.split(':')[-1]
                name = link.split('/')[-1]
                jivochat.send_photo(chat_id, tracking_data['NAME'], link, name, 'viber')
    except IOError:
        logger.info("File not accessible")
    all_filenames = [i for i in glob.glob(f'media/{chat_id}/*.jpg')]
    for i in all_filenames:
        f = open(i ,'rb')
        os.remove(i)
    try:
        open(f'media/{chat_id}/links.txt', 'w').close()
        open(f'media/{chat_id}/history.txt', 'w').close()
    except:
        pass


@logger.catch
def user_message_handler(viber, viber_request):
    """Receiving a message from user and sending replies."""
    logger.info(viber_request)
    message = viber_request.message
    tracking_data = message.tracking_data
    chat_id = viber_request.sender.id
    # Data for usual TextMessage
    reply_text = ''
    reply_keyboard = {}
    # Data for RichMediaMessage
    reply_alt_text = ''
    reply_rich_media = {}
    tracking_data = json.loads(tracking_data)
    data_keys = {'NAME': 'ViberUser', 'HISTORY': '', 'CHAT_MODE': 'off', 'STAGE': 'menu', 'PHOTO_MODE': 'off'}
    for k in data_keys:
        if k not in tracking_data:
            tracking_data[k] = data_keys[k]

    if isinstance(message, ContactMessage):
        # Handling reply after user shared his contact infromation
        if 'PHONE' in tracking_data:
            reply_keyboard = kb.operator_keyboard
            reply_text = resources.specify_deal_id
            tracking_data['STAGE'] = 'deal'
        else:
            tracking_data['PHONE'] = message.contact.phone_number
            deals_grabber(message.contact.phone_number, chat_id, tracking_data, viber)
    elif isinstance(message, PictureMessage):
        response = requests.get(viber_request.message.media)
        if not os.path.exists(f'media/{chat_id}'):
            os.makedirs(f'media/{chat_id}')
        img_path = f"media/{chat_id}/{viber_request.message_token}.jpg"
        with open(img_path, 'wb') as f:
            f.write(response.content)
        link = upload_image(img_path)
        if tracking_data['CHAT_MODE'] == 'on':
            payload = json.loads(jsonpickle.encode(viber_request.message))
            jivochat.send_photo(chat_id, tracking_data['NAME'],
                                link,
                                'user_image',
                                'viber')
        else:
            file_links = open(f'media/{chat_id}/links.txt', 'a')
            file_links.write(f'{tracking_data["STAGE"]}:{link},')
            file_links.close()
            if tracking_data['STAGE'] == 'receipt':
                reply_keyboard = kb.photo_keyboard
                reply_text = resources.photo_choice_message
                tracking_data['STAGE'] = ''
                tracking_data['PHOTO_MODE'] == 'on'
            elif tracking_data['STAGE'] == 'passport':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.inn_message
                tracking_data['STAGE'] = 'inn'
                tracking_data['PHOTO_MODE'] == 'on'
            elif tracking_data['STAGE'] == 'inn':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.guarantee_message
                tracking_data['STAGE'] = 'guarantee'
                tracking_data['PHOTO_MODE'] == 'on'
            elif tracking_data['STAGE'] == 'guarantee':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.pamyatka_message
                tracking_data['STAGE'] = 'pamyatka'
                tracking_data['PHOTO_MODE'] == 'on'
            elif tracking_data['STAGE'] == 'pamyatka':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.condition_message
                tracking_data['STAGE'] = 'condition'
                tracking_data['PHOTO_MODE'] == 'off'
            else:
                tracking_data['STAGE'] = ''
            save_message_to_history(reply_text, 'bot', chat_id)
            logger.info(tracking_data)
            tracking_data = json.dumps(tracking_data)
            reply = [TextMessage(text=reply_text,
                                 keyboard=reply_keyboard,
                                 tracking_data=tracking_data,
                                 min_api_version=3)]
            viber.send_messages(chat_id, reply)
    else:
        text = viber_request.message.text
        save_message_to_history(text, 'user', chat_id)
        if text == 'end_chat':
            tracking_data['CHAT_MODE'] = 'off'
        if tracking_data['CHAT_MODE'] == 'on':
            payload = json.loads(jsonpickle.encode(viber_request.message))
            if 'media' in payload:
                jivochat.send_photo(chat_id, tracking_data['NAME'],
                                    viber_request.message.media,
                                    viber_request.message_token,
                                    'viber')
            else:
                jivochat.send_message(chat_id, tracking_data['NAME'],
                                      text,
                                      'viber')
            reply_keyboard = kb.end_chat_keyboard

        else:
            if text == 'menu':
                reply_keyboard = kb.menu_keyboard
                reply_text = resources.menu_message
                try:
                    open(f'media/{chat_id}/history.txt', 'w').close()
                except:
                    pass
            elif text == 'end_chat':
                jivochat.send_message(chat_id,
                                      tracking_data['NAME'],
                                      jivosource.user_ended_chat,
                                      'viber')
                answer = [TextMessage(text=resources.chat_ending)]
                viber.send_messages(chat_id, answer)
                reply_keyboard = kb.menu_keyboard
                reply_text = resources.menu_message
                time.sleep(1)
            elif text == 'operator':
                tracking_data['CHAT_MODE'] = 'on'
                operator_connection(chat_id, tracking_data)
                reply_keyboard = kb.end_chat_keyboard
                reply_text = resources.operator_message
                tracking_data['HISTORY'] = ''
            elif text == 'repair':
                reply_keyboard = kb.confirmation_keyboard
                reply_text = resources.repair_message
            elif text == 'paid':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.payment_message
                add_task(chat_id, tracking_data['DEAL'][0][0], tracking_data['DEAL'][0][1], tracking_data['PHONE'])
            elif text == 'register':
                if task_active():
                    answer = [TextMessage(text=resources.payment_message)]
                    viber.send_messages(chat_id, answer)
                    reply_keyboard = kb.menu_keyboard
                    reply_text = resources.menu_message
                    time.sleep(1)
                else:
                    if 'DEAL' in tracking_data and len(tracking_data['DEAL']) > 0:
                        status = str(get_deal_by_id(tracking_data['DEAL'][0][0]))
                        logger.info(status)
                        if status == '209':
                            reply_keyboard = kb.operator_keyboard
                            reply_text = resources.rozetka_link
                            tracking_data['STAGE'] = 'rozetka'
                        else:
                            pay_link = get_link_by_id(tracking_data['DEAL'][0][0])
                            if pay_link:
                                reply_keyboard = kb.pay_keyboard
                                reply_text = resources.link_message.replace('[string]', pay_link)
                            else:
                                reply_keyboard = kb.operator_keyboard
                                reply_text = resources.deal_error
                    else:
                        reply_keyboard = kb.operator_keyboard
                        reply_text = resources.deal_error
            elif text == 'continue':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.name_message
                tracking_data['STAGE'] = 'contact'
            elif text == 'upload':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.passport_message
                tracking_data['STAGE'] = 'passport'
            elif text == 'guarantee':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.guarantee_message
                tracking_data['STAGE'] = 'guarantee'
            else:
                if tracking_data['STAGE'] == 'phone':
                    if text[:3] == '380' and len(text) == 12:
                        if 'PHONE' in tracking_data:
                            reply_keyboard = kb.operator_keyboard
                            reply_text = resources.specify_deal_id
                            tracking_data['STAGE'] = 'deal'
                        else:
                            tracking_data['PHONE'] = text
                            contact_id = check_phone(text)
                            if contact_id:
                                logger.info('Found contact_id')
                                logger.info(contact_id)
                                deals = find_deal_by_contact(contact_id[0][1])
                                logger.info(deals)
                                tracking_data['DEALS'] = deals
                                if len(deals) == 0 or len(deals) > 1:
                                    reply_keyboard = kb.operator_keyboard
                                    reply_text = resources.specify_deal_id
                                    tracking_data['STAGE'] = 'deal'
                                else:
                                    reply_keyboard = kb.menu_keyboard
                                    reply_text = resources.menu_message
                                    tracking_data['DEAL'] = deals[0]
                            else:
                                logger.info('Not found contact_id')
                                reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
                                reply_text = resources.phone_error
                                tracking_data['STAGE'] = 'phone'
                                logger.info(tracking_data)
                    else:
                        reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
                        reply_text = resources.phone_error
                elif tracking_data['STAGE'] == 'deal':
                    if len(text) == 9:
                        result = []
                        for item in tracking_data['DEALS']:
                            if text == item[1]:
                                tracking_data['DEAL'] = item
                                result.append(item)
                        if result:
                            reply_keyboard = kb.menu_keyboard
                            reply_text = resources.menu_message
                        else:
                            deal_id = find_deal_by_title(text)
                            if deal_id != []:
                                tracking_data['DEAL'] = deal_id
                                reply_keyboard = kb.menu_keyboard
                                reply_text = resources.menu_message
                                tracking_data['STAGE'] = 'menu'
                            else:
                                tracking_data['CHAT_MODE'] = 'on'
                                operator_connection(chat_id, tracking_data)
                                reply_keyboard = kb.end_chat_keyboard
                                reply_text = resources.operator_message
                                tracking_data['HISTORY'] = ''
                    else:
                        reply_keyboard = kb.operator_keyboard
                        reply_text = resources.deal_error
                elif tracking_data['STAGE'] == 'menu':
                    reply_keyboard = kb.menu_keyboard
                    reply_text = resources.menu_message
                    try:
                        open(f'media/{chat_id}/history.txt', 'w').close()
                    except:
                        pass
                elif tracking_data['PHOTO_MODE'] == 'on':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'contact':
                    tracking_data['NAME'] = text
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.phone_message
                    tracking_data['STAGE'] = 'city'
                elif tracking_data['STAGE'] == 'city':
                    tracking_data['PHONE'] = text
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.city_message
                    tracking_data['STAGE'] = 'brand'
                elif tracking_data['STAGE'] == 'brand':
                    tracking_data['CITY'] = text
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.brand_message
                    tracking_data['STAGE'] = 'serial'
                elif tracking_data['STAGE'] == 'serial':
                    tracking_data['BRAND'] = text
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.serial_message
                    tracking_data['STAGE'] = 'receipt'
                elif tracking_data['STAGE'] == 'condition':
                    tracking_data['CONDITION'] = text
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.detail_message
                    tracking_data['STAGE'] = 'detail'
                elif tracking_data['STAGE'] == 'detail':
                    tracking_data['DETAIL'] = text
                    reply_keyboard = kb.return_keyboard
                    reply_text = resources.finish_message
                    tracking_data['STAGE'] = ''
                ################################################################
                elif tracking_data['STAGE'] == 'receipt':
                    tracking_data['SERIAL'] = text
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.receipt_message
                    tracking_data['PHOTO_MODE'] == 'on'
                elif tracking_data['STAGE'] == 'guarantee':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'passport':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'inn':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'pamyatka':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'rozetka':
                    if 'rozetka.com.ua' in text:
                        title = ''
                        try:
                            title = str(get_product_title(text)) + '\n'
                        except Exception as e:
                            logger.info(e)
                    reply_keyboard = kb.operator_keyboard
                    reply_text = title + resources.wait_for_operator
                else:
                    reply_keyboard = kb.menu_keyboard
                    reply_text = resources.menu_message
                    tracking_data['STAGE'] = 'menu'
            save_message_to_history(reply_text, 'bot', chat_id)
            logger.info(tracking_data)
            tracking_data = json.dumps(tracking_data)
            reply = [TextMessage(text=reply_text,
                                 keyboard=reply_keyboard,
                                 tracking_data=tracking_data,
                                 min_api_version=6)]
            viber.send_messages(chat_id, reply)
