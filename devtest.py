from bitrix import crm_tools

# import http.client
# conn = http.client.HTTPConnection("ifconfig.me")
# conn.request("GET", "/ip")
# print(conn.getresponse().read())

if __name__ == '__main__':
    chat_id = '+XS2XxGhTunlRnOPpEl2NQ=='
    tracking_data = {'PHONE': 1111111111}
    crm_tools.send_to_erp(tracking_data, chat_id)
