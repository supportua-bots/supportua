from bitrix.crm_tools import find_contact_by_phone, get_deal_by_id, get_open_products

# import http.client
# conn = http.client.HTTPConnection("ifconfig.me")
# conn.request("GET", "/ip")
# print(conn.getresponse().read())

if __name__ == '__main__':
    # print(get_deal_by_id('31411'))
    print(get_open_products('31411'))
