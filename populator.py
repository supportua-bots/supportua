from db_func.database import input_new_users, create_table
from bitrix.crm_tools import find_contact_by_phone
from loguru import logger


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


if __name__ == '__main__':
    create_table()
    contacts = find_contact_by_phone()
    logger.info(f'{len(input_new_users(contacts))} new contacts added.')
