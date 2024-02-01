# app.py
import math
import string
import random
import sys
import time
import os
import asyncio

from gevent.pywsgi import WSGIServer
from flask import Flask, render_template
from flask_socketio import SocketIO
import qrcode
from database.sql_provider import SQLProvider

########################################
import pandas as pd
import numpy as np

# Укажите путь к вашему файлу Excel
path_to_project = sys.argv[0]

index = path_to_project.rfind("\\")  # Находим индекс последнего слэша

print(f'path_to_project[index + 1:] = {path_to_project[:index + 1]}')
path_to_project = path_to_project[:index + 1]
excel_path = path_to_project + 'JackBox.xlsx'
print(f'excel_path = {excel_path}')

# Прочтите данные из файла Excel
df = pd.read_excel(excel_path)

# Выведите первые несколько строк данных для проверки
print(f'df.head() = \n{df.head()}')

print(f'df = \n{df}')

print(f'df[1, 1] = \n{df.iat[0, 7]}')

print(pd.isnull(df.iat[0, 7]))

index = 1
question = df.iloc[index][:3].to_dict()
question['variants'] = df.iloc[index][3:].dropna().tolist()

print(f'question = {question}')

print(question['image'])

# print(f'question = {question}')

########################################

print(f"before app")

app = Flask(__name__)
socketio = SocketIO(app)

print(f"after app")

@app.route('/')
def index():
    # return render_template('index.html')
    return render_template('question.html', question=question)


# @app.route('/question')
# def question(number):



if __name__ == '__main__':
    # print('cum')
    # try:
    # port = os.environ['PORT']
    # print(f"port = {os.environ}")
    # http_server = WSGIServer(('0.0.0.0', int(port)), app)
    # http_server.serve_forever()
    # except KeyError:
    # socketio.run(app, debug=True, host='0.0.0.0')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)