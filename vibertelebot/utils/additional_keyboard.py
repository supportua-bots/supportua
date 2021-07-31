import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from textskeyboards import viberkeyboards as kb

dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

MAIN_COLOR = os.getenv("COLOR")


SHARE_PHONE_KEYBOARD = {
    "DefaultHeight": False,
    "BgColor": '#f7f9fc',
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": MAIN_COLOR,
            "BgLoop": True,
            "ActionType": "share-phone",
            "ActionBody": kb.phone_keyboard[0][1],
            "ReplyType": "message",
            "Text": kb.phone_keyboard[0][0],
            # "TextOpacity": 0,
            "Image": kb.phone_keyboard[0][2]
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": MAIN_COLOR,
            "BgLoop": True,
            "ActionType": "share-phone",
            "ActionBody": kb.phone_keyboard[1][1],
            "ReplyType": "message",
            "Text": kb.phone_keyboard[1][0],
            # "TextOpacity": 0,
            "Image": kb.phone_keyboard[1][2]
        },
    ]
}


MENU_BUTTON = {
        "Columns": 6,
        "Rows": 1,
        "BgColor": MAIN_COLOR,
        "BgLoop": True,
        "ActionType": "reply",
        "ActionBody": kb.deal_keyboard[1],
        "ReplyType": "message",
        "Text": kb.deal_keyboard[0],
        # "TextOpacity": 0,
}
