from bitrix.crm_tools import find_contact_by_phone, get_deal_by_id, get_open_products, find_deal_by_phone_direct, find_deal_by_contact

# import http.client
# conn = http.client.HTTPConnection("ifconfig.me")
# conn.request("GET", "/ip")
# print(conn.getresponse().read())

if __name__ == '__main__':
    id = find_deal_by_phone_direct('0982031573')
    if id:
        print(find_deal_by_contact(id))
