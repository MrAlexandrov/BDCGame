import os
from typing import Optional, Dict

from flask import (
    Blueprint, request,
    render_template, current_app,
    session, redirect, url_for
)

from db_work import select_dict
from db_work import select
from sql_provider import SQLProvider

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
    if request.method == 'GET':
        return render_template('login.html', message='')
    else:
        login = request.form.get('login')
        password = request.form.get('password')

        print(f'provider = {provider}')
        sql_login = provider.get('login.sql', login=login, password=password)
        print(f'sql_login: {sql_login}')
        user_info = select_dict(current_app.config['db_config'], sql_login)
        if len(user_info) == 0:
            return render_template('login.html', message='Неверный логин или пароль')
        # return render_template('login.html', message=f'Вы вошли как {user_info[0][0][0]}')
        user_dict = user_info[0]
        print(f'user_dict {user_dict}')
        print(f'user_info {user_info}')
        print(user_dict['user_id'])
        print(f'user_id {user_dict["user_id"]}, user_group {user_dict["user_group"]}')
        session['user_id'] = user_dict['user_id']
        session['user_group'] = user_dict['user_group']
        session.permanent = True
        return redirect(url_for('blueprint_admin.start_game'))

        # if login and password:
        #     # Получаем информацию о разных пользователях с таким логином и паролем.
        #     user_info = define_user(login, password)
        #     if user_info:
        #         # Берём первого (единственного) пользователя с таким логином и паролем.
        #         user_dict = user_info[0]
        #         # Записываем в сессию полученную из БД информацию о пользователе.
        #         # session.clear()
        #         session['user_id'] = user_dict['user_id']
        #         session['user_group'] = user_dict['user_group']
        #         session.permanent = True
        #         return redirect(url_for('menu_choice'))
        #     else:   # Не нашёлся пользователь с такими данными.
        #         return render_template('input_login.html', message='Неверный логин или пароль')
        # return render_template('input_login.html', message='Повторите ввод')


# В случае нахождения пользователя с такими, данными возвращает лист словарей.
# Каждый словарь - набор информации о конкретном пользователе.
# def define_user(login: str, password: str) -> Optional[Dict]:
#     # Получаем готовые запросы.
#     sql_internal = provider.get('login.sql', login=login, password=password)
#     sql_external = provider.get('external_user.sql', login=login, password=password)
#
#     user_info = None
#
#     for sql_search in [sql_internal, sql_external]:
#         _user_info = select_dict(current_app.config['db_config'], sql_search)
#         if _user_info:
#             user_info = _user_info
#             del _user_info
#             break
#     return user_info