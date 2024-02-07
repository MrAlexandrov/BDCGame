import os

from flask import (
    Blueprint, request,
    render_template, current_app,
    session, redirect, url_for
)
from db_work import select
from sql_provider import SQLProvider
from access import group_required


blueprint_admin = Blueprint('blueprint_admin', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_admin.route('/', methods=['GET', 'POST'])
@group_required
def start_game():
    if request.method == 'POST':
        # Флаг, что игра теперь запущена
        current_app.config['work'] = True
        return render_template('admin_panel.html')
    return render_template('start_game.html')