import functools
import subprocess
from flask import Flask, request, Response, json, jsonify
from multiprocessing import Process
from threading import Thread
# from telegrambot import main as tgbot
from jivochat import main as jivo
from vibertelebot import main as vbbot
from addons.populator import launch as taskfunel
from db_func.database import create_table
from loguru import logger
from waitress import serve


app = Flask(__name__)

# with app.app_context():
#     try:
#         create_table()
#         background_process = Process(target=taskfunel).start()
#     except KeyboardInterrupt:
#         background_process.terminate()
#         background_process.join()


# def error_handler(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         while True:
#             try:
#                 return func(*args, **kwargs)
#             except Exception:
#                 subprocess.call(
#                     ["bash", "/var/www/chatboto/supportua/restart"])
#     return wrapper


@app.route('/jivochatviber', methods=['GET', 'POST'])
def jivochat_endpoint_viber():
    source = 'viber'
    data = request.get_json()
    logger.info(data)
    Thread(target=jivo.main, args=(data, source)).start()
    returned_data = {'result': 'ok'}
    response = app.response_class(
        response=json.dumps(returned_data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/viber', methods=['POST'])
def viber_endpoint():
    source = 'viber'
    vbbot.main(request)
    return Response(status=200)


def server_launch():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    try:
        create_table()
        background_process = Process(target=taskfunel).start()
        flask_server = Process(target=server_launch).start()
    except KeyboardInterrupt:
        flask_server.terminate()
        background_process.terminate()
        flask_server.join()
        background_process.join()
