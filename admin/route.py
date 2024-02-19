import os
import sys

from flask import (
    Blueprint, request,
    render_template, current_app,
    session, redirect, url_for
)
from db_work import select
from sql_provider import SQLProvider
from access import group_required
from flask_socketio import SocketIO, emit
import pandas as pd


blueprint_admin = Blueprint('blueprint_admin', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


# current_app.register_blueprint(blueprint_admin, url_prefix='/admin')


@blueprint_admin.route('/', methods=['GET', 'POST'])
@group_required
def admin():
    current_app.config['admin_logged_in'] = True
    print(f'Admin logged in render admin.html')
    return render_template('admin.html')


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
    print('Admin get question')
    question = df.iloc[index][:3].to_dict()
    question['variants'] = df.iloc[index][3:].dropna().tolist()
    return question


def get_next_question():
    print('Admin get next question')
    current_app.config['number_question'] += 1
    current_app.config['question'] = get_question(current_app.config['number_question'])
    return current_app.config['question']


def register_admin_socketio_handlers(socketio):
# Логика WebSocket для начала игры и следующего вопроса
    @socketio.on('start_game_admin')
    def handle_start_game_admin():
        print('Python admin handle start game')
        current_app.config['work'] = True
        emit('startGameBtn')

    @socketio.on('admin_next_question')
    def handle_next_question_admin():
        print('Admin handle next question')
        print(f'Before current_app.config[\'number_question\'] {current_app.config["number_question"]}')
        get_next_question()
        print(f'After current_app.config[\'number_question\'] {current_app.config["number_question"]}')
        # Добавьте здесь логику для отображения следующего вопроса, например, запрос из базы данных
        emit('new_question', {'question': current_app.config['question']}, broadcast=True)
        return current_app.config['question']

    # @socketio.on('app_get_current_question')
    # def get_current_question():
    #     print('Admin get current question')
    #     return current_app.config['question']