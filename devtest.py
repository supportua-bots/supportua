from bitrix import crm_tools

# import http.client
# conn = http.client.HTTPConnection("ifconfig.me")
# conn.request("GET", "/ip")
# print(conn.getresponse().read())

if __name__ == '__main__':
    deals = ['24975', '24963', '22813']
    if crm_tools.check_open_deals(deals):
        print('Luck')
