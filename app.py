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
from access import login_required, group_required, external_required

# from auth.route import blueprint_auth
# from admin.route import blueprint_admin
# from game.route import blueprint_game

import qrcode
from database.sql_provider import SQLProvider


app = Flask(__name__)
app.secret_key = 'SuperKey'
socketio = SocketIO(app)


# app.register_blueprint(blueprint_auth, url_prefix='/auth')
# app.register_blueprint(blueprint_admin, url_prefix='/admin')
# app.register_blueprint(blueprint_game, url_prefix='/game')

app.config['db_config'] = json.load(open('configs/db_config.json'))
app.config['access_config'] = json.load(open('configs/access.json'))
app.config['cache_config'] = json.load(open('configs/cache.json'))
app.config['report_url'] = json.load(open('configs/report_url.json'))
app.config['report_list'] = json.load(open('configs/report_list.json', encoding='UTF-8'))

# Флаг, что игра не запущена
app.config['work'] = False


@app.route('/', methods=['GET', 'POST'])
@login_required                     # Если пользователь не залогинен, откроется страница авторизации
def index():
    if session.get('user_group') == "admin":
        return redirect(url_for('blueprint_admin.start_game'))
    return redirect(url_for('blueprint_game.game'))
    # return render_template('index.html')
    # return render_template('question.html', question=question)


# @app.route('/question')
# def question(number):


########################################
import pandas as pd
import numpy as np

# Укажите путь к вашему файлу Excel
path_to_project = sys.argv[0]

index = path_to_project.rfind("\\")  # Находим индекс последнего слэша

print(f'path_to_project[index + 1:] = {path_to_project[:index + 1]}')
path_to_project = path_to_project[:index + 1]
excel_path = path_to_project + 'JackBox.xlsx'
print(f'excel_path = {excel_path}')

# Прочтите данные из файла Excel
df = pd.read_excel(excel_path)

# Выведите первые несколько строк данных для проверки
print(f'df.head() = \n{df.head()}')

print(f'df = \n{df}')

print(f'df[1, 1] = \n{df.iat[0, 7]}')

print(pd.isnull(df.iat[0, 7]))

index = 0
question = df.iloc[index][:3].to_dict()
question['variants'] = df.iloc[index][3:].dropna().tolist()

print(f'question = {question}')

print(question['image'])

# print(f'question = {question}')

########################################


@socketio.on('start_game')
def handle_start_game():
    # Логика для начала игры
    # Отправить сообщение всем игрокам о начале игры
    socketio.emit('game_started', {'action': 'game_started'}, broadcast=True)


@socketio.on('start_game')
def handle_start_game():
    # Обработка события начала игры
    # Здесь вы можете отправить первый вопрос игрокам
    # Пример:
    question_data = {}  # Ваши данные для первого вопроса
    emit('next_question', question_data, broadcast=True)



if __name__ == '__main__':
    # try:
    # port = os.environ['PORT']
    # print(f"port = {os.environ}")
    # http_server = WSGIServer(('0.0.0.0', int(port)), app)
    # http_server.serve_forever()
    # except KeyError:
    # socketio.run(app, debug=True, host='0.0.0.0')

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)