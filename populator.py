from db_func.database import input_new_users, create_table
from bitrix.crm_tools import find_contact_by_phone


if __name__ == '__main__':
    create_table()
    contacts = find_contact_by_phone()
    print(input_new_users(contacts))
