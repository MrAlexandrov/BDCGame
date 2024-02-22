import os
import sys

from flask import (
    Blueprint, request,
    render_template, current_app,
    session, redirect, url_for
)
from db_work import select
from sql_provider import SQLProvider
from access import login_required, group_required
from db_work import select
from flask_socketio import emit
import pandas as pd
import datetime


blueprint_admin = Blueprint('blueprint_admin', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


# current_app.register_blueprint(blueprint_admin, url_prefix='/admin')


@blueprint_admin.route('/', methods=['GET', 'POST'])
@login_required
@group_required
def admin():
    current_app.config['admin_logged_in'] = True
    print(f'admin\\route: Admin logged in render admin.html')
    return render_template('admin.html',
                           game_started=current_app.config['work'],
                           current_page=current_app.config['current_page'])


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
    return question


def get_prev_question():
    print('admin\\route: Admin get previous question')
    if current_app.config['number_question'] > 1:
        current_app.config['number_question'] -= 1
    current_app.config['question'] = get_question(current_app.config['number_question'])
    return current_app.config['question']


def get_next_question():
    print('admin\\route: Admin get next question')
    current_app.config['number_question'] += 1
    current_app.config['question'] = get_question(current_app.config['number_question'])
    return current_app.config['question']


def register_admin_socketio_handlers(socketio):
# Логика WebSocket для начала игры и следующего вопроса
    @socketio.on('LoadPack')
    def handle_load_pack():
        print(f'admin\\route: Load Pack')
        return None

    @socketio.on('start_game_admin')
    def handle_start_game_admin():
        print('admin\\route: start_game_admin')
        current_app.config['work'] = True
        emit('render_waiting_room_gamer')

    @socketio.on('admin_prev_question')
    def handle_prev_question_admin():
        print('admin\\route: Admin handle prev question')
        print(f'admin\\route: Before current_app.config[\'number_question\'] {current_app.config["number_question"]}')
        get_prev_question()
        print(f'admin\\route: After current_app.config[\'number_question\'] {current_app.config["number_question"]}')
        # Добавьте здесь логику для отображения следующего вопроса, например, запрос из базы данных
        current_app.config['current_page'] = current_app.config['question']
        emit('new_question', {'question': current_app.config['current_page']}, broadcast=True)
        return current_app.config['question']

    @socketio.on('admin_current_question')
    def handle_current_question_admin():
        print('admin\\route: Admin handle current question')
        current_app.config['current_page'] = current_app.config['question']
        emit('new_question', {'question': current_app.config['current_page']}, broadcast=True)
        return current_app.config['question']

    @socketio.on('admin_next_question')
    def handle_next_question_admin():
        print('admin\\route: Admin handle next question')
        print(f'admin\\route: Before current_app.config[\'number_question\'] {current_app.config["number_question"]}')
        get_next_question()
        print(f'admin\\route: After current_app.config[\'number_question\'] {current_app.config["number_question"]}')
        # Добавьте здесь логику для отображения следующего вопроса, например, запрос из базы данных
        current_app.config['current_page'] = current_app.config['question']
        # current_time = datetime.datetime.now()
        emit('new_question', {'question': current_app.config['current_page']}, broadcast=True)
        return current_app.config['question']

    @socketio.on('admin_break')
    def handle_break_admin():
        print('admin\\route: break admin')
        current_app.config['current_page'] = current_app.config['break']
        emit('new_question', {'question': current_app.config['current_page']}, broadcast=True)
        return current_app.config['break']

    @socketio.on('admin_results')
    def handle_results_admin():
        print('admin\\route: results admin')
        sql_results = provider.get('results.sql')
        results_info = select(current_app.config['db_config'], sql_results)
        print(f'results_info: {results_info}')
        current_app.config['results']['table'][0] = results_info[0]
        current_app.config['current_page'] = current_app.config['results']
        emit('new_question', {'question': current_app.config['current_page']}, broadcast=True)

    @socketio.on('admin_lock_buttons')
    def handle_lock_buttons_admin():
        print('admin\\route: lock buttons admin')
        emit('lock_buttons', broadcast=True)

    @socketio.on('admin_exit')
    def handle_admin_exit():
        print(f'admin\\route: handle admin exit')
        emit('user_exit', broadcast=True)

# Обработчик для WebSocket соединения
    @socketio.on('connect')
    def handle_connect():
        print('admin\\route: admin connected')

    # Обработчик для WebSocket соединения
    @socketio.on('disconnect')
    def handle_disconnect():
        print('admin\\route: admin disconnected')