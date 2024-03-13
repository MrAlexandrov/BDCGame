import os
import sys

from flask import Blueprint, current_app, render_template, redirect, url_for, session

from access import group_required, login_required
from sql_provider import SQLProvider


from flask_socketio import emit

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
    # session.clear()
    print(f'game\\route: session = {session}')
    if current_app.config['work']:
        if session.get('user_group') == 'gamer':
            return render_template('gamer_page.html', question=current_app.config['current_page'])
        else:
            print(f'game\\route: User should be logged in and user should be gamer')
    # print(f'game current_app.config[\'question\'] = {current_app.config["question"]}')
    return render_template('gamer_page.html', question=current_app.config['current_page'])


def register_game_socketio_handlers(socketio):
    @socketio.on('render_waiting_room_gamer')
    def render_waiting_room_gamer():
        print(f'game\\route: render_waiting_room_gamer')
        return render_template('waiting_game.html')

    # @socketio.on('start_game_gamer')
    # def handle_start_game():
    #     print('game\\route: start_game_gamer')
    #     # return redirect(url_for('/'))

    def add_answer(answer):
        print(f'game\\route: Add answer')
        print(f'game\\route: answer = {answer}')
        # answer=str(answer)
        user_id = session['user_id']
        question_number = current_app.config['number_question']
        sql_add_answer = provider.get('add_answer.sql',
                                      user_id=user_id,
                                      question_number=question_number,
                                      answer=answer)
        insert(current_app.config['db_config'], sql_add_answer)
        print(f'game\\route: End add answer')

    @socketio.on('text_answer')
    def text_answer(data):
        print(f'game\\route: text_answer = {data}')
        team_name = session['team_name']
        if len(data) == 0:
            return None
        answer = data['text']
        if len(answer) == 0:
            return None
        team_name = session['team_name']
        user_id = session['user_id']
        question_number = current_app.config['number_question']
        print(f'game\\route: team_name = {team_name}')
        print(f'game\\route: id = {question_number}')
        print(f'game\\route: answer = {answer}')
        add_answer(answer)

        if answer == current_app.config['right_answers'][question_number]:
            sql_increase_score = provider.get('increase_score.sql', user_id=user_id)
            update(current_app.config['db_config'], sql_increase_score)

    @socketio.on('clicked_buttons')
    def clicked_buttons(data):
        print(f'game\\route: data = {data}')
        print(f'game\\route: session = {session}')
        # print(f'game\\route: session[\'team_name\'] = {session['team_name']}')
        print(f'game\\route: session[\'user_id\'] = {session['user_id']}')
        if len(data['clickedButtons']) == 0 or len(data['clickedButtons'][0]) == 0:
            return None
        print(f'game\\route: data[\'clickedButtons\'] = {data['clickedButtons']}')
        # team_name = session['team_name']
        user_id = session['user_id']
        question_number = current_app.config['number_question']
        list_answers = []
        for i in range(len(data['clickedButtons'])):
            answer = data['clickedButtons'][i]['text']
            print(f'game\\route: answer = {answer}')
            # # button_number = data['clickedButtons'][i]['id']
            # print(f'game\\route: team_name = {team_name}')
            print(f'game\\route: id = {question_number}')
            print(f'game\\route: answer = {answer}')
            list_answers.append(answer)
            add_answer(answer)
        if sorted(list_answers) == current_app.config['right_answers'][question_number]:
            sql_increase_score = provider.get('increase_score.sql', user_id=user_id)
            print(f'game\\route: sql_increase_score = {sql_increase_score}')
            update(current_app.config['db_config'], sql_increase_score)
            # sql_right_answer = provider.get('right_answer.sql', question_number=question_number)
            # print(f'game\\route: sql_right_answer = {sql_right_answer}')
            # temp = select(current_app.config['db_config'], sql_right_answer)
            # print(f'game\\route: temp = {temp}')
            # if len(temp[0]) == 0:
            #     return None
            # check = temp[0][0][0]
            # print(f'game\\route: check = {check}')
            # if answer == check:
            #     sql_increase_score = provider.get('increase_score.sql', team_name=team_name)
            #     print(f'game\\route: sql_increase_score = {sql_increase_score}')
            #     update(current_app.config['db_config'], sql_increase_score)



    # Отправка нового вопроса всем клиентам
    @socketio.on('game_next_question')
    def handle_next_question():
        print(f'game\\route: handle next question current_app.config[\'question\'] = {current_app.config["question"]}')
        # emit('next_question', {'question': current_app.config['question']}, broadcast=True)
        # return render_template('gamer_page.html', question=current_app.config['question'])

    @socketio.on('game_prev_question')
    def handle_prev_question():
        print(f'game\\route: handle next question current_app.config[\'question\'] = {current_app.config["question"]}')
        # emit('next_question', {'question': current_app.config['question']}, broadcast=True)
        # return render_template('gamer_page.html', question=current_app.config['question'])




    @socketio.on('gamer_exit')
    def handle_gamer_exit():
        print(f'game\\route: handle gamer exit')
        print(f'game\\route: session = {session}')
        session.clear()
        print(f'game\\route: session = {session}')
        redirect(url_for('blueprint_auth.start_auth'))

    # Обработчик для WebSocket соединения
    @socketio.on('connect')
    def handle_connect():
        print('game\\route: Client connected')


    # Обработчик для WebSocket соединения
    @socketio.on('disconnect')
    def handle_disconnect():
        print('game\\route: Client disconnected')