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
from multiprocessing import Process
from datetime import date, datetime, timedelta
from textskeyboards import texts as resources
from vibertelebot.utils.tools import (keyboard_consctructor,
                                      deal_keyboard_consctructor,
                                      product_keyboard_consctructor,
                                      save_message_to_history,
                                      workdays, divide_chunks)
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.contact_message import ContactMessage
from viberbot.api.messages.location_message import LocationMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.messages.video_message import VideoMessage
from jivochat import sender as jivochat
from jivochat.utils import resources as jivosource
from bitrix.crm_tools import (find_deal_by_contact, send_model_field, send_to_erp,
                              find_deal_by_title, upload_image, get_deal_by_id, get_link_by_id,
                              check_open_deals, get_deal_product, get_link_product,
                              get_open_products, get_product_data)
from db_func.database import check_phone, add_user, add_task
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
def get_info_from_page(deal, text):
    parsing_result = get_product_data(text)
    send_model_field(tracking_data['DEAL'],
                     parsing_result[0],
                     parsing_result[1],
                     text)


@logger.catch
def deals_grabber(phone, chat_id, tracking_data, viber):
    contact_id = check_phone(phone)
    if contact_id:
        logger.info(contact_id)
        deals = find_deal_by_contact(contact_id[0][0])
        logger.info(f'Deals: {deals}')
        if len(deals) == 0:
            reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
            reply_text = resources.deal_error
            tracking_data['STAGE'] = 'phone'
            logger.info(tracking_data)
        elif len(deals) > 1:
            text_deals = ','.join(deals)
            add_user(tracking_data['PHONE'],
                     chat_id,
                     text_deals,
                     tracking_data['NAME'])
            if check_open_deals(text_deals):
                reply_keyboard = kb.menu_keyboard
            else:
                reply_keyboard = kb.part_menu_keyboard
            reply_text = resources.menu_message
            tracking_data['DEALS'] = text_deals
            tracking_data['STAGE'] = 'menu'
        else:
            add_user(tracking_data['PHONE'],
                     chat_id,
                     deals[0],
                     tracking_data['NAME'])
            if check_open_deals(deals[0]):
                reply_keyboard = kb.menu_keyboard
            else:
                reply_keyboard = kb.part_menu_keyboard
            reply_text = resources.menu_message
            tracking_data['DEALS'] = deals[0]
    else:
        reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
        reply_text = resources.deal_error
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
            if content:
                links = content.split(',')
                for link in links:
                    link = link.split('@')[-1]
                    name = link.split('/')[-1]
                    jivochat.send_photo(
                        chat_id, tracking_data['NAME'], link, name, 'viber')
    except IOError:
        logger.info("File not accessible")
    all_filenames = [i for i in glob.glob(f'media/{chat_id}/*.jpg')]
    for i in all_filenames:
        f = open(i, 'rb')
        os.remove(i)
    try:
        open(f'media/{chat_id}/links.txt', 'w').close()
        open(f'media/{chat_id}/history.txt', 'w').close()
    except:
        pass


@logger.catch
def user_message_handler(viber, viber_request):
    """Receiving a message from user and sending replies."""
    background_process = None
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
    data_keys = {'NAME': 'ViberUser', 'HISTORY': '', 'CHAT_MODE': 'off',
                 'STAGE': 'menu', 'PHOTO_MODE': 'off', 'DEALS': ''}
    for k in data_keys:
        if k not in tracking_data:
            tracking_data[k] = data_keys[k]

    if isinstance(message, ContactMessage):
        # Handling reply after user shared his contact infromation
        if message.contact.name:
            tracking_data['NAME'] = message.contact.name
        if 'PHONE' in tracking_data:
            reply_keyboard = kb.operator_keyboard
            reply_text = resources.specify_deal_id
            tracking_data['STAGE'] = 'deal'
        else:
            tracking_data['PHONE'] = message.contact.phone_number
            deals_grabber(message.contact.phone_number,
                          chat_id, tracking_data, viber)
    elif isinstance(message, VideoMessage):
        jivochat.send_video(chat_id, tracking_data['NAME'],
                            viber_request.message.media,
                            viber_request.message_token,
                            'viber')
    elif isinstance(message, PictureMessage):
        response = requests.get(viber_request.message.media)
        if not os.path.exists(f'media/{chat_id}'):
            os.makedirs(f'media/{chat_id}')
        if tracking_data['PHOTO_MODE'] == 'on':
            img_path = f"media/{chat_id}/{tracking_data['STAGE']}.jpg"
        else:
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
            file_links.write(f'{tracking_data["STAGE"]}@{link},')
            file_links.close()
            if tracking_data['STAGE'] == 'receipt':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.guarantee_message
                tracking_data['STAGE'] = 'warranty'
                tracking_data['PHOTO_MODE'] == 'on'
            # elif tracking_data['STAGE'] == 'passport1':
            #     reply_keyboard = kb.operator_keyboard
            #     reply_text = resources.passport_two_message
            #     tracking_data['STAGE'] = 'passport2'
            #     tracking_data['PHOTO_MODE'] == 'on'
            # elif tracking_data['STAGE'] == 'passport2':
            #     reply_keyboard = kb.operator_keyboard
            #     reply_text = resources.passport_eleven_message
            #     tracking_data['STAGE'] = 'passport11'
            #     tracking_data['PHOTO_MODE'] == 'on'
            # elif tracking_data['STAGE'] == 'passport11':
            #     reply_keyboard = kb.operator_keyboard
            #     reply_text = resources.inn_message
            #     tracking_data['STAGE'] = 'inn'
            #     tracking_data['PHOTO_MODE'] == 'on'
            # elif tracking_data['STAGE'] == 'inn':
            #     reply_keyboard = kb.operator_keyboard
            #     reply_text = resources.guarantee_message
            #     tracking_data['STAGE'] = 'warranty'
            #     tracking_data['PHOTO_MODE'] == 'on'
            elif tracking_data['STAGE'] == 'warranty':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.condition_message
                tracking_data['STAGE'] = 'condition'
                tracking_data['PHOTO_MODE'] = 'off'
            # elif tracking_data['STAGE'] == 'memo':
            #     reply_keyboard = kb.operator_keyboard
            #     reply_text = resources.condition_message
            #     tracking_data['STAGE'] = 'condition'
            #     tracking_data['PHOTO_MODE'] = 'off'
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
                if check_open_deals(tracking_data['DEALS']):
                    reply_keyboard = kb.menu_keyboard
                else:
                    reply_keyboard = kb.part_menu_keyboard
                reply_text = resources.menu_message
                try:
                    open(f'media/{chat_id}/history.txt', 'w').close()
                except:
                    pass
            elif text == 'phone_share':
                reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
                reply_text = resources.greeting_message
                tracking_data['STAGE'] = 'phone'
            elif text == 'end_chat':
                jivochat.send_message(chat_id,
                                      tracking_data['NAME'],
                                      jivosource.user_ended_chat,
                                      'viber')
                answer = [TextMessage(text=resources.chat_ending)]
                viber.send_messages(chat_id, answer)
                if check_open_deals(tracking_data['DEALS']):
                    reply_keyboard = kb.menu_keyboard
                else:
                    reply_keyboard = kb.part_menu_keyboard
                reply_text = resources.menu_message
                time.sleep(1)
            elif text == 'operator':
                tracking_data['CHAT_MODE'] = 'on'
                operator_connection(chat_id, tracking_data)
                reply_keyboard = kb.end_chat_keyboard
                reply_text = resources.operator_message
                tracking_data['HISTORY'] = ''
            elif text[:4] == 'deal':
                reply_keyboard = kb.confirmation_keyboard
                reply_text = resources.repair_message
                deal_id = text.split('-')[1]
                product = get_deal_product(deal_id)
                tracking_data['BRAND'] = product
            elif text == 'repair':
                keyboard = []
                deals = tracking_data['DEALS'].split(',')
                for deal in deals:
                    item = get_deal_product(deal)
                    logger.info(f"Title: {item}")
                    if not item:
                        product_link = get_link_product(deal)
                        logger.info(f"Link: {product_link}")
                        if not product_link:
                            item = 'Нет информации о товаре.'
                        else:
                            valid_link = product_link.split(',')[0]
                            logger.info(f"Valid: {valid_link}")
                            if 'rozetka.com.ua' in valid_link:
                                try:
                                    parsing_result = get_product_title(
                                        valid_link)
                                    logger.info(
                                        f"Parsing: {str(parsing_result)}")
                                    item = str(parsing_result[0])
                                except Exception as e:
                                    item = 'Нет информации о товаре'
                                    logger.info(e)
                    keyboard.append([item, deal])
                reply_text = resources.choose_product_message
                reply_keyboard = deal_keyboard_consctructor(keyboard)
            elif text == 'rozetka':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.rozetka_link
                tracking_data['STAGE'] = 'rozetka'
            elif text[:7] == 'product':
                deal_id = text.split('-')[1]
                tracking_data['DEAL'] = deal_id
                status = str(get_deal_by_id(deal_id))
                logger.info(status)
                if status == '209':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.rozetka_link
                    tracking_data['STAGE'] = 'rozetka'
                else:
                    tracking_data['CHAT_MODE'] = 'on'
                    operator_connection(chat_id, tracking_data)
                    reply_keyboard = kb.end_chat_keyboard
                    reply_text = resources.payment_error
                    tracking_data['HISTORY'] = ''
            elif text == 'register':
                products = get_open_products(tracking_data['DEALS'])
                reply_text = resources.choose_product_message
                reply_keyboard = product_keyboard_consctructor(products)
                tracking_data['PRODUCT'] = products
            elif text == 'continue':
                reply_keyboard = kb.operator_keyboard
                reply_text = resources.name_message
                tracking_data['STAGE'] = 'contact'
            # elif text == 'upload':
            #     reply_keyboard = kb.operator_keyboard
            #     reply_text = resources.guarantee_message
            #     tracking_data['STAGE'] = 'warranty'
            # elif text == 'warranty':
            #     reply_keyboard = kb.operator_keyboard
            #     reply_text = resources.guarantee_message
            #     tracking_data['STAGE'] = 'warranty'
            else:
                if tracking_data['STAGE'] == 'phone':
                    if text[:3] == '380' and len(text) == 12:
                        tracking_data['PHONE'] = text
                        deals_grabber(text, chat_id, tracking_data, viber)
                        return
                    else:
                        reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
                        reply_text = resources.phone_error
                elif tracking_data['STAGE'] == 'menu':
                    if check_open_deals(tracking_data['DEALS']):
                        reply_keyboard = kb.menu_keyboard
                    else:
                        reply_keyboard = kb.part_menu_keyboard
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
                    tracking_data['STAGE'] = 'serial'
                elif tracking_data['STAGE'] == 'serial':
                    tracking_data['CITY'] = text
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
                    send_to_erp(tracking_data, chat_id)
                    tracking_data['STAGE'] = ''

                ################################################################
                elif tracking_data['STAGE'] == 'receipt':
                    tracking_data['SERIAL'] = text
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.receipt_message
                    tracking_data['PHOTO_MODE'] = 'on'
                elif tracking_data['STAGE'] == 'warranty':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'passport1':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'passport2':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'passport11':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'inn':
                    reply_keyboard = kb.operator_keyboard
                    reply_text = resources.not_photo_error_message
                # elif tracking_data['STAGE'] == 'memo':
                #     reply_keyboard = kb.operator_keyboard
                #     reply_text = resources.not_photo_error_message
                elif tracking_data['STAGE'] == 'rozetka':
                    if 'rozetka.com.ua' in text:
                        try:
                            title = get_product_title(text)
                        except Exception as e:
                            logger.info(e)
                    if title:
                        reply = [TextMessage(text=title)]
                        viber.send_messages(chat_id, reply)
                        time.sleep(0.5)
                        reply_keyboard = kb.parsing_keyboard
                        reply_text = resources.key_wait
                        add_task(chat_id,
                                 tracking_data['DEAL'],
                                 tracking_data['PHONE'])
                        tracking_data['STAGE'] = 'menu'
                        background_process = Process(target=get_info_from_page, args=(
                            tracking_data['DEAL'], text)).start()
                    else:
                        reply_keyboard = kb.parsing_error_keyboard
                        reply_text = resources.rozetka_link_error
                else:
                    if check_open_deals(tracking_data['DEALS']):
                        reply_keyboard = kb.menu_keyboard
                    else:
                        reply_keyboard = kb.part_menu_keyboard
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
            if background_process:
                background_process.join()
