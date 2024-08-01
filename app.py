import json
import math
import string
import random
import sys
import time
import os
import asyncio

from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, redirect, url_for, session, current_app
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

# Загрузка конфигурационных файлов
try:
    with open('configs/db_config.json') as config_file:
        config_content = config_file.read().strip()
        if not config_content:
            raise ValueError("db_config.json is empty")
        app.config['db_config'] = json.loads(config_content)
except Exception as e:
    print(f"Error loading db_config.json: {e}")

try:
    with open('configs/access.json') as access_config_file:
        config_content = access_config_file.read().strip()
        if not config_content:
            raise ValueError("access.json is empty")
        app.config['access_config'] = json.loads(config_content)
except Exception as e:
    print(f"Error loading access.json: {e}")

try:
    with open('configs/cache.json') as cache_config_file:
        config_content = cache_config_file.read().strip()
        if not config_content:
            raise ValueError("cache.json is empty")
        app.config['cache_config'] = json.loads(config_content)
except Exception as e:
    print(f"Error loading cache.json: {e}")

# app.config['report_url'] = json.load(open('configs/report_url.json'))
# app.config['report_list'] = json.load(open('configs/report_list.json', encoding='UTF-8'))

# Флаг, что игра не запущена
app.config['work'] = False
app.config['admin_logged_in'] = False

app.config['begin'] = {
    'number': 0,
    'question': 'Подключайтесь к игре!',
    'image': '0.png',
    'type': 'info',
    'variants': [],
    'lock': False,
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
        qr_data = f"http://{local_ip}:5000"
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

def get_excel():
    # Укажите путь к вашему файлу Excel
    path_to_project = sys.argv[0]

    index = path_to_project.rfind("\\")  # Находим индекс последнего слэша

    path_to_project = path_to_project[:index + 1]
    excel_path = path_to_project + 'JackBox_piter.xlsx'

    # Прочтите данные из файла Excel
    df = pd.read_excel(excel_path)

    return df

df = get_excel()

def get_question(index):
    print('app\\route: Admin get question')
    question = df.iloc[index][:3].to_dict()
    question['variants'] = df.iloc[index][3:].dropna().tolist()
    question['type'] = 'multi'
    question['lock'] = False
    question['answer'] = []
    return question

@socketio.on('load_pack')
def load_pack():
    questions = []
    right_answers = []
    for i in range(len(df)):
        current_question = get_question(i)
        current_right_answers = []
        if len(current_question['variants']) == 1:
            current_question['type'] = 'text'
            current_question['answer'].append(current_question['variants'])
            current_right_answers.append(current_question['variants'][0])
        else:
            for j in range(len(current_question['variants'])):
                ans = current_question['variants'][j]
                if ans[0] == '!':
                    current_question['variants'][j] = ans[1:]
                    current_right_answers.append(current_question['variants'][j])
                    current_question['answer'].append(current_question['variants'][j])
            if len(current_right_answers) == 1:
                current_question['type'] = 'single'
            if len(current_right_answers) > 1:
                current_right_answers.sort()
                current_question['type'] = 'multi'
        questions.append(current_question)
        right_answers.append(current_right_answers)

    app.config['questions'] = questions
    app.config['right_answers'] = right_answers
    print('admin\\route:', '-' * 150)
    print('admin\\route: questions', *app.config['questions'], sep='\n')
    print('admin\\route:', '-' * 150)
    print('admin\\route: right_answers', *app.config['right_answers'], sep='\n')
    print('admin\\route:', '-' * 150)
    return questions

app.config['number_question'] = 0

@app.errorhandler(404)
def page_not_found(e):
    # Здесь можно возвращать специальную страницу для ошибки 404
    return redirect(url_for('blueprint_auth.start_auth'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
