import os
from typing import Optional, Dict

from flask import (
    Blueprint, request,
    render_template, current_app,
    session, redirect, url_for
)

from db_work import select_dict, select, insert
from sql_provider import SQLProvider
# from flask_login import current_user

##### СОЗДАНИЕ BLUEPRINT'а #####
# 'admin' – имя Blueprint, которое будет суффиксом ко всем именам методов, данного модуля;
# __name__ – имя исполняемого модуля, относительно которого будет искаться папка admin и соответствующие подкаталоги;
# template_folder – подкаталог для шаблонов данного Blueprint (необязательный параметр, при его отсутствии берется подкаталог шаблонов приложения);
# static_folder – подкаталог для статических файлов (необязательный параметр, при его отсутствии берется подкаталог static приложения).
# После создания эскиза его нужно зарегистрировать в основном приложении.

blueprint_auth = Blueprint('blueprint_auth', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_auth.route('/', methods=['GET', 'POST'])
def start_auth():
    if session.get('user_group') == 'admin':
        print(f'auth\\route: User is admin')
        current_app.config['admin_logged_in'] = True
        return redirect(url_for('blueprint_admin.admin'))
    # session.clear()
    if request.method == 'GET':
        print(f'GET request')
        if not current_app.config['admin_logged_in']:   # Если администратор не залогинен, нужно, чтобы тот появился
            if session.get('user_group') == 'gamer':
                return render_template('login.html', header='Пожалуйста, подождите, когда подключится администратор', admin=False, message='')
            print(f'auth\\route: Admin is not logged in, render admin auth')
            return render_template('login.html', header='Вход для администратора', admin=True, message='')
        else:           # Администратор залогинен
            if session.get('user_group') == 'admin':    # Если это сессия админа
                print(f'auth\\route: Admin has logged in, and user is admin, redirect to admin page')
                return redirect(url_for('blueprint_admin.admin'))
            elif session.get('user_group') == 'gamer':
                print(f'auth\\route: session = {session}')
                print(f'auth\\route: Admin has logged in, and user is gamer, redirect to gamer page')
                return redirect(url_for('blueprint_game.game'))
            else:
                print(f'auth\\route: Admin has logged in, user has no group, render authorisation')
                return render_template('login.html', header='Введите название команды', admin=False, message='')
    else:
        print(f'auth\\route: POST request')
        login = request.form.get('login')
        password = request.form.get('password')

        if password:
            print(f'auth\\route: Password is {password}, login is {login}')
            sql_login = provider.get('login.sql', login=login, password=password)
            user_info = select_dict(sql_login)
            if len(user_info) == 0:
                return render_template('login.html', header='Вход для администратора', admin=True, message='')
            user_dict = user_info[0]
            session['user_id'] = user_dict['user_id']
            session['user_group'] = user_dict['user_group']
            session.permanent = True
            current_app.config['admin_logged_in'] = True
            return redirect(url_for('blueprint_admin.admin'))
        else:
            print(f'auth\\route: Password empty, it is gamer authorisation')
            if session.get('user_group') == 'gamer':
                return redirect(url_for('blueprint_game.game'))
            sql_check_team = provider.get('check_team.sql', login=login)
            print(f'auth\\route: Check team query = {sql_check_team}')
            check_team_table = select(sql_check_team)
            print(f'auth\\route: Query result = {check_team_table}')
            if len(check_team_table) == 0:
                print(f'auth\\route: No such team, creating such team login = {login}')
                sql_new_team = provider.get('new_team.sql', login=login)
                insert(sql_new_team)
                sql_get_id = provider.get('get_id.sql', login=login)
                print(f'auth\\route: sql_get_id = {sql_get_id}')
                print(f"auth\\route: user_id will be = {select(sql_get_id)[0][0]}")
                session['user_id'] = select(sql_get_id)[0][0]
                session['user_group'] = 'gamer'
                session['login'] = login
                session.permanent = False
                print(f'auth\\route: session = {session}')
                print(f"auth\\route: session['login'] = {session['login']}")
                return redirect(url_for('blueprint_game.game'))
            else:
                print(f'auth\\route: Team already exist')
                return render_template('login.html', header='Введите название команды', admin=False, message='Такая команда уже существует')
