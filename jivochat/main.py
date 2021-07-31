import os
import re
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot
from telegram.utils.request import Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.viber_requests import (ViberFailedRequest,
                                         ViberConversationStartedRequest,
                                         ViberMessageRequest,
                                         ViberSubscribedRequest)
from vibertelebot.utils.tools import keyboard_consctructor
from vibertelebot.main import viber
from flask import Flask, request, Response, json, jsonify
from jivochat.utils import resources
from loguru import logger
from db_func.database import check_user
from textskeyboards import viberkeyboards as kb


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")

bot = Bot(token=os.getenv("TOKEN"))


def main(data, source):
    if 'event_name' not in data:
        if data['message']['type'] == 'text':
            user = data['recipient']['id']
            user_info  = check_user(user)
            logger.info(user_info)
            if user_info:
                username = user_info[0][4]
                phone = user_info[0][1]
                deal = user_info[0][3]
            else:
                username = 'ViberUser'
                phone = ''
                deal = ''
            logger.info(user)
            text = data['message']['text']
            logger.info(text)
            tracking_data = {'NAME': username,
                             'HISTORY': '',
                             'CHAT_MODE': 'on',
                             'STAGE': 'menu',
                             'PHOTO_MODE': 'off',
                             'DEAL': deal,
                             'PHONE': phone}
            tracking_data = json.dumps(tracking_data)
            keyboard = [('Завершити чат', 'end_chat')]
            reply_keyboard = keyboard_consctructor(keyboard)
            viber.send_messages(user, [TextMessage(text=text,
                                                   keyboard=reply_keyboard,
                                                    tracking_data=tracking_data)])
        if data['message']['type'] == 'photo':
            user = data['recipient']['id']
            user_info  = check_user(user)
            logger.info(user_info)
            if user_info:
                username = user_info[0][4]
                phone = user_info[0][1]
                deal = user_info[0][3]
            else:
                username = 'ViberUser'
                phone = ''
                deal = ''
            logger.info(user)
            link = data['message']['file']
            tracking_data = {'NAME': username,
                             'HISTORY': '',
                             'CHAT_MODE': 'on',
                             'STAGE': 'menu',
                             'PHOTO_MODE': 'off',
                             'DEAL': deal,
                             'PHONE': phone}
            tracking_data = json.dumps(tracking_data)
            keyboard = [('Завершити чат', 'end_chat')]
            reply_keyboard = keyboard_consctructor(keyboard)
            viber.send_messages(user, [PictureMessage(text='',
                                                    keyboard=reply_keyboard,
                                                    tracking_data=tracking_data,
                                                    media=link)])
    else:
        user_id = str(re.findall(f'\[(.*?)\]', data['visitor']['name'])[0])
        user_info  = check_user(user_id)
        if user_info:
            username = user_info[0][4]
            phone = user_info[0][1]
            deal = user_info[0][3]
        else:
            username = 'ViberUser'
            phone = ''
            deal = ''
        logger.info(user)
        text = data['message']['text']
        logger.info(text)
        tracking_data = {'NAME': username,
                         'HISTORY': '',
                         'CHAT_MODE': 'on',
                         'STAGE': 'menu',
                         'PHOTO_MODE': 'off',
                         'DEAL': deal,
                         'PHONE': phone}
        tracking_data = json.dumps(tracking_data)
        if data['event_name'] == 'chat_accepted':
            keyboard = [('Завершити чат', 'end_chat')]
            reply_keyboard = keyboard_consctructor(keyboard)
            viber.send_messages(user_id, [TextMessage(text=resources.operator_connected,
                                                   keyboard=reply_keyboard,
                                                    tracking_data=tracking_data)])
        if data['event_name'] == 'chat_finished':
            if resources.user_ended_chat not in str(data['plain_messages']):
                viber.send_messages(user_id, [TextMessage(text=resources.operator_ended_chat)])
                time.sleep(1)
                viber.send_messages(user_id, [TextMessage(text=resources.menu_message,
                                                       keyboard=kb.menu_keyboard,
                                                        tracking_data=tracking_data)])
    returned_data = {'result': 'ok'}
    return returned_data
