import os
import sys

from flask import Blueprint, current_app, render_template, redirect, url_for, session

from access import group_required, login_required
from sql_provider import SQLProvider


from flask_socketio import SocketIO, emit

from db_work import insert, select, update

blueprint_game = Blueprint('blueprint_game', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
# current_app.register_blueprint(blueprint_game, url_prefix='/game')


@blueprint_game.route('/', methods=['GET', 'POST'])
@login_required
# @group_required
def game():
    # print(f'We are in game current_app.config[\'work\'] = {current_app.config["work"]}')
    # # Если игра не запущена, нужно загрузить страницу ожидания
    # if not current_app.config['work']:
    #     return render_template('waiting_game.html')
    # if current_app.config['work']:
    #     session['user_id'] = 1
    #     session['user_group'] = 'gamer'
    #     session.permanent = True
    #     return redirect(url_for('blueprint_game.game'))
    print(f'game current_app.config[\'question\'] = {current_app.config["question"]}')
    return render_template('single_choice_question.html', question=current_app.config['question'])


def register_game_socketio_handlers(socketio):
    @socketio.on('start_game')
    def handle_start_game():
        # current_app.config['work'] = True
        print('Python game start game')
        # gamer_autorisation = render_template('create_team.html')
        # Добавьте здесь логику для начала игры, например, изменение статуса игры в базе данных
        emit('start_game', {'load_creating_team': ''}, broadcast=True)


    @socketio.on('clicked_buttons')
    def clicked_buttons(data):
        print(f'data = {data}')
        team_name = session['team_name']
        if len(data['clickedButtons']) == 0:
            return None
        button_number = data['clickedButtons'][0]['id']
        question_number = current_app.config['number_question']
        answer = data['clickedButtons'][0]['text']
        print(f'team_name = {team_name}')
        print(f'id = {question_number}')
        print(f'answer = {answer}')
        if len(data['clickedButtons'][0]):
            sql_add_answer = provider.get('add_answer.sql', team_name=team_name, question_number=question_number, answer=answer)
            insert(current_app.config['db_config'], sql_add_answer)

        sql_right_answer = provider.get('right_answer.sql', question_number=question_number)
        print(f'sql_right_answer = {sql_right_answer}')
        check = select(current_app.config['db_config'], sql_right_answer)[0][0][0]
        print(f'check = {check}')
        if (answer == check):
            sql_increase_score = provider.get('increase_score.sql', team_name=team_name)
            print(f'sql_increase_score = {sql_increase_score}')
            update(current_app.config['db_config'], sql_increase_score)
        # print(f'data = {data}')
        # print(f'session = {session}')




    # Отправка нового вопроса всем клиентам
    @socketio.on('game_next_question')
    def handle_next_question():
        print(f'handle next question current_app.config[\'question\'] = {current_app.config["question"]}')
        emit('next_question', {'question': current_app.config['question']}, broadcast=True)
        return render_template('single_choice_question.html', question=current_app.config['question'])


    # @socketio.on('new_question')
    # def handle_new_question():
    #     print(f'handle new question in game')
    #     current_app.config['number_question'] += 1
    #     current_app.config['question'] = get_current_question(current_app.config['number_question'])
    #     return render_template('single_choice_question.html', question=current_app.config['question'])


    # @socketio.on('next_question')
    # def handle_next_question():
    #     return render_template('single_choice_question.html', question=current_app.config['question'])


    # Обработчик для WebSocket соединения
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')


    # Обработчик для WebSocket соединения
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')