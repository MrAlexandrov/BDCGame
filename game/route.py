import os
import sys

from flask import Blueprint, current_app, render_template

from access import group_required
from sql_provider import SQLProvider


from app import socketio


blueprint_game = Blueprint('blueprint_game', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
# current_app.register_blueprint(blueprint_game, url_prefix='/game')


@blueprint_game.route('/', methods=['GET', 'POST'])
@group_required
def game():
    # Если игра не запущена, нужно загрузить страницу ожидания
    if not current_app.config['work']:
        return render_template('waiting_game.html')

    # Игра уже идет, загружаем страницу с вопросом
    return render_template('single_choice_question.html', question=question)