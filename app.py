# app.py
import math
import string
import random
import sys
import time
import os
import asyncio

from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, redirect, url_for, json, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from access import login_required, group_required, external_required

from auth.route import blueprint_auth
from admin.route import blueprint_admin, register_admin_socketio_handlers
from game.route import blueprint_game, register_game_socketio_handlers

import pandas as pd
import numpy as np

import qrcode
import socket
from database.sql_provider import SQLProvider


app = Flask(__name__)
print(f'app = {app}')
app.secret_key = 'SuperKey'
socketio = SocketIO(app)
register_admin_socketio_handlers(socketio)
register_game_socketio_handlers(socketio)
CORS(app)

app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_admin, url_prefix='/admin')
app.register_blueprint(blueprint_game, url_prefix='/game')

app.config['db_config'] = json.load(open('configs/db_config.json'))
app.config['access_config'] = json.load(open('configs/access.json'))
app.config['cache_config'] = json.load(open('configs/cache.json'))
app.config['report_url'] = json.load(open('configs/report_url.json'))
app.config['report_list'] = json.load(open('configs/report_list.json', encoding='UTF-8'))

# Флаг, что игра не запущена
app.config['work'] = False
app.config['admin_logged_in'] = False

app.config['begin'] = {
    'number': 0,
    'question': 'Подключайтесь к игре!',
    'image': '0.png',
    'type': 'info',
    'variants': [],
    'table': []
}

app.config['number_question'] = 0
app.config['current_page'] = app.config['begin']

app.config['break'] = {
    'number': 0,
    'question': 'Перекур!',
    'image': 'break.jpg',
    'type': 'info',
    'variants': [],
    'table': []
}

app.config['results'] = question_data = {
        "number": 0,
        "question": "Результаты",
        "image": "results.jpg",
        "type": "info",
        "variants": [],
        "table": [
            [("Команда 1", 10), ("Команда 2", 8), ("Команда 3", 6)],
            ["Место", "Название команды", "Счет"]
        ]
    }


# @app.before_request
# def clear_session():
#     session.modified = True

# Получаем локальный ip для запуска приложения на localhost
def get_local_ip():
    try:
        # Создаем временный сокет
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))  # Подключаемся к любому хосту
        local_ip = temp_socket.getsockname()[0]  # Получаем IP-адрес
        temp_socket.close()  # Закрываем временный сокет
        return local_ip
    except Exception as e:
        print("Error while getting local IP:", e)
        return None


# Генерируем qr-код на основе локального адреса
def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)


# Функция для создания qr-кода, по которому можно подключиться к игре
# TODO: Добавить возможность создавать qr-код не только для локального хоста
def make_qr():
    local_ip = get_local_ip()
    if local_ip:
        print("app\\route: Local IP Address:", local_ip)
        qr_data = f"{local_ip}:5000"
        generate_qr_code(qr_data, "static/images/0.png")
        return local_ip
    else:
        print("app\\route: Failed to retrieve local IP address.")
        return None


make_qr()


@app.route('/', methods=['GET', 'POST'])
def index():
    # session.clear()
    current_user = session.get('user_group')
    if current_user:
        print(f'app\\route: User is logged in')
        if current_user == "admin":
            print(f'app\\route: User is admin')
            app.config['admin_logged_in'] = True
            return redirect(url_for('blueprint_admin.admin'))
        # elif current_user == 'gamer':
        #     print(f'User is gamer')
        #     return redirect(url_for('blueprint_gamer.game'))
    return redirect(url_for('blueprint_auth.start_auth'))


@app.route('/exit')
# @login_required
def exit_func():
    session.clear()
    if session.get('user_group') == "admin":
        app.config['admin_logged_in'] = False
    return redirect(url_for('blueprint_auth.start_auth'))


def get_exel():
    # Укажите путь к вашему файлу Excel
    path_to_project = sys.argv[0]

    index = path_to_project.rfind("\\")  # Находим индекс последнего слэша

    # print(f'path_to_project[index + 1:] = {path_to_project[:index + 1]}')
    path_to_project = path_to_project[:index + 1]
    excel_path = path_to_project + 'JackBox.xlsx'
    # print(f'excel_path = {excel_path}')

    # Прочтите данные из файла Excel
    df = pd.read_excel(excel_path)

    return df


df = get_exel()


def get_question(index):
    print('admin\\route: Admin get question')
    question = df.iloc[index][:3].to_dict()
    question['variants'] = df.iloc[index][3:].dropna().tolist()
    question['type'] = 'single'
    question['lock'] = False
    return question


@socketio.on('load_pack')
def load_pack():
    questions = []
    for i in range(len(df)):
        questions.append(get_question(i))

    app.config['questions'] = questions
    print('admin\\route: questions', *app.config['questions'], sep='\n')
    return questions


app.config['number_question'] = 0

########################################


# @socketio.on('app_get_current_question')
# def get_current_question():
#     print(f'app\\route: app_get_current_question')
#     return app.config['current_page']


# @socketio.on('app_get_next_question')
# def get_next_question():
#     print(f'app\\route: app_get_next_question')
#     app.config['number_question'] += 1
#     app.config['question'] = get_question(app.config['number_question'])
#     return app.config['question']

# TODO: Сделать эту штуку
# @socketio.on('startGame')
# def start_game():
#     print(f'app\\route: start_game')
#     socketio.emit('start_game_admin')
#     print(f'app\\route: after start_game_admin')
#     emit('start_game_gamer')


@app.errorhandler(404)
def page_not_found(e):
    # Здесь можно возвращать специальную страницу для ошибки 404
    return redirect(url_for('blueprint_auth.start_auth'))

if __name__ == '__main__':
    # try:
    # port = os.environ['PORT']
    # print(f"port = {os.environ}")
    # http_server = WSGIServer(('0.0.0.0', int(port)), app)
    # http_server.serve_forever()
    # except KeyError:
    # socketio.run(app, debug=True, host='0.0.0.0')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
