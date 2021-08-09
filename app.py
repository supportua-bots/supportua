from flask import Flask, request, Response, json, jsonify
from multiprocessing import Process
# from telegrambot import main as tgbot
from jivochat import main as jivo
from vibertelebot import main as vbbot
from populator import launch as taskfunel
from db_func.database import create_table
from loguru import logger
from waitress import serve


app = Flask(__name__)


@app.route('/jivochatviber', methods=['GET', 'POST'])
def jivochat_endpoint_viber():
    source = 'viber'
    data = request.get_json()
    logger.info(data)
    returned_data = jivo.main(data, source)
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
    app.run(host='0.0.0.0')
    serve(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    try:
        create_table()
        main_server = Process(target=server_launch).start()
        background_process = Process(target=taskfunel).start()
    except KeyboardInterrupt:
        main_server.terminate()
        background_process.terminate()
        main_server.join()
        background_process.join()
