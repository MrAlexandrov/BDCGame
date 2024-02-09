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

from flask_socketio import SocketIO

from app import socketio


blueprint_admin = Blueprint('blueprint_admin', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
# current_app.register_blueprint(blueprint_admin, url_prefix='/admin')


@blueprint_admin.route('/', methods=['GET', 'POST'])
@group_required
def start_game():
    # if request.method == 'POST':
    if current_app.config['work']:
        return render_template('admin_panel.html')

    # Флаг, что игра теперь запущена
    current_app.config['work'] = True
    return render_template('start_game.html')