import json
from db_func.database import get_all_tasks
from bitrix.crm_tools import get_deal_by_id
from viberbot.api.messages.text_message import TextMessage
from vibertelebot.main import viber
from textskeyboards import viberkeyboards as kb
from textskeyboards import texts as resources
from loguru import logger


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def check_payment_status():
    tasks = get_all_tasks()
    for task in tasks:
        status = str(get_deal_by_id(task[1]))
        logger.info(f'Checking payment status for {str(task)}')
        if status == '209':
            tracking_data = {'NAME': 'ViberUser',
                             'HISTORY': '',
                             'CHAT_MODE': 'off',
                             'STAGE': 'rozetka',
                             'PHOTO_MODE': 'off',
                             'DEAL': [[task[1], task[2]]],
                             'PHONE': task[3]}
            reply_keyboard = kb.operator_keyboard
            reply_text = resources.rozetka_link
            tracking_data = json.dumps(tracking_data)
            reply = [TextMessage(text=reply_text,
                                 keyboard=reply_keyboard,
                                 tracking_data=tracking_data,
                                 min_api_version=6)]
            viber.send_messages(task[0], reply)


if __name__ == '__main__':
    check_payment_status()
