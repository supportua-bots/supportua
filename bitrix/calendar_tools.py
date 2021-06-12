import os
import base64
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime, date, timedelta
from bitrix.admin import OWNER_ID, SECTION_ID
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


URL = f'https://supportua.bitrix24.ua/rest/2067/2ganq1hgz5etn112/calendar.event.get.json?type=company_calendar&ownerId=U_115&section={SECTION_ID}'

time_chunks = ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30']


@logger.catch
def workdays(d, end, excluded=(6, 7)):
    days = []
    while d.date() <= end.date():
        if d.isoweekday() not in excluded:
            days.append(d)
        d += timedelta(days=1)
    return days[1:21]


@logger.catch
def time_table_creator():
    timetable = {}
    list_of_dates = workdays(datetime.now(), datetime.now() + timedelta(days=30))
    for date in list_of_dates:
        stringified_date = date.strftime('%Y-%m-%d')
        for time_period in time_chunks:
            datetime_string = f'{stringified_date} {time_period}'
            beautified_date = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')
            timestamp_start = datetime.timestamp(beautified_date)
            timestamp_end = datetime.timestamp(beautified_date + timedelta(minutes=30))
            if stringified_date in timetable:
                timetable[stringified_date].append([time_period, timestamp_start, timestamp_end])
            else:
                timetable[stringified_date] = [[time_period, timestamp_start, timestamp_end]]
    return timetable


@logger.catch
def calendar_grabber():
    x = requests.get(URL)
    answer = x.json()
    event_list = []
    for event in answer['result']:
        date_start = float(event['DATE_FROM_TS_UTC']) + 10800.0
        date_end = float(event['DATE_TO_TS_UTC']) + 10800.0
        event_list.append((date_start, date_end))
    return event_list


@logger.catch
def schedule_matcher():
    static_schedule = time_table_creator()
    # print(static_schedule)
    event_list = calendar_grabber()
    empty_dates = []
    for day in static_schedule:
        delete_items = []
        for period in static_schedule[day]:
            for event in event_list:
                if (event[0] < period[1] and period[1] < event[1]) or (event[0] >= period[1] and event[1] >= period[2] and event[0] < period[2]):
                    delete_items.append(period)
        for item in delete_items:
            try:
                static_schedule[day].remove(item)
            except:
                pass
        if not static_schedule[day]:
            empty_dates.append(day)
    for item in empty_dates:
        print(static_schedule.pop(item, None))
    available_dates = sorted(static_schedule.items())
    return available_dates


@logger.catch
def add_event(start, end, name, deal_id):
    link = f'https://supportua.bitrix24.ua/crm/deal/details/{deal_id}/'
    SEND_URL = f'https://supportua.bitrix24.ua/rest/2067/h77kc3hpgxie6dxl/calendar.event.add.json?type=company_calendar&ownerId=U_115&from_ts={int(start)}&to_ts={int(end)}&section={SECTION_ID}&name={name}&is_meeting=Y&attendees[]=355&attendees[]=78&attendees[]=383&attendees[]=178&attendees[]=253&attendees[]=2067&description={link}'
    x = requests.get(SEND_URL)


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


if __name__ == '__main__':
    url = "https://api.imgbb.com/1/upload"
    api_key = os.getenv('IMAGE_API')
    path = 'photo2870.jpg'
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    params = {
        'key': api_key,
        'image': encoded_string
    }
    r = requests.post(url, data=params)
    print(r.json()['data']['url'])
    print(r.text)
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
