from db_func.database import input_new_users, create_table
from bitrix.crm_tools import find_contact_by_phone
from loguru import logger


if __name__ == '__main__':
    create_table()
    contacts = find_contact_by_phone()
    new_users = input_new_users(contacts)
    logger.info(f'{len(new_users)} new contacts added.')
    logger.info(new_users)
