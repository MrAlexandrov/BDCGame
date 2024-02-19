from typing import Tuple, List
from db_context_manager import DBContextManager


# Возвращает результат выполнения sql-запроса в виде двух листов - заголовка и содержимого.
def select(db_config: dict, sql: str) -> Tuple[Tuple, List[str]]:
    """
    Выполняет запрос (SELECT) к БД с указанным конфигом и запросом.
    Args:
        db_config: dict - Конфиг для подключения к БД.
        sql: str - SQL-запрос.
    Return:
        Кортеж с результатом запроса и описанеим колонок запроса.
    """
    # schema - заголовки результирующей таблицы.
    schema = []
    # result - Все остальные строки результирующей таблицы.
    result = tuple()
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        cursor.execute(sql)
        schema = [column[0] for column in cursor.description]
        result = cursor.fetchall()
    return result, schema


# Возвращает результат (набор строк) выполнения sql-запроса к бд, подключенной по db_config
# В виде словаря.
# def select_dict(db_config: dict, sql: str) -> dict:
def select_dict(db_config: dict, sql: str):
    result = []
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        cursor.execute(sql)
        schema = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            result.append(dict(zip(schema, row)))
    return result


def insert(db_config: dict, sql: str):
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        result = cursor.execute(sql)
    return result


def update(db_config: dict, sql: str):
    """
    Выполняет запрос (UPDATE) к БД с указанным конфигом и запросом.
    Args:
        db_config: dict - Конфиг для подключения к БД.
        sql: str - SQL-запрос.
    Return:
        Результат выполнения запроса.
    """
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        cursor.execute(sql)
        # Если нужно получить результат выполнения, можно использовать cursor.rowcount
        # Пример: result = cursor.rowcount
    return  # Если есть результат выполнения, его можно вернуть



def call_proc(db_config: dict, proc_name: str, *args):
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        param_list = []
        for arg in args:
            param_list.append(arg)

        res = cursor.callproc(proc_name, param_list)
        # print(f"res = {res}")
    return res