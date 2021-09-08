import schedule
import time
from db_func.database import input_new_users, create_table
from bitrix.crm_tools import find_contact_by_phone
from addons.tasks import task_checker
from loguru import logger


@logger.catch
def launch():
    create_table()
    while 1:
        try:
            contacts = find_contact_by_phone()
            if contacts is not None:
                # logger.info(contacts)
                new_users = input_new_users(contacts)
                logger.info(f'{len(new_users)} new contacts added.')
                logger.info(new_users)
        except Exception as e:
            logger.warning(e)
        finally:
            task_checker()
            time.sleep(300)


if __name__ == '__main__':
    launch()
