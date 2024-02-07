import os

from flask import Blueprint, current_app, render_template

from access import group_required
from sql_provider import SQLProvider

blueprint_game = Blueprint('blueprint_game', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_game.route('/', methods=['GET', 'POST'])
@group_required
def game():
    # Если игра не запущена, нужно загрузить страницу ожидания,
    # можно добавить QR-код, чтобы показывать соседям
    if current_app.config['work'] == False:
        return render_template('waiting_game.html')

    # Игра уже идёт
    return render_template('game.html')