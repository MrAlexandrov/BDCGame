from db_context_manager import DBContextManager

def select(query, params=None):
    """
    Выполняет SQL-запрос и возвращает все результаты в виде списка кортежей.
    """
    with DBContextManager() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def select_dict(query, params=None):
    """
    Выполняет SQL-запрос и возвращает все результаты в виде списка словарей.
    """
    with DBContextManager() as cursor:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def insert(query, params=None):
    """
    Выполняет SQL-запрос для вставки данных и возвращает ID последней вставленной записи.
    """
    with DBContextManager() as cursor:
        cursor.execute(query, params)
        # return cursor.fetchone()[0]

def update(query, params=None):
    """
    Выполняет SQL-запрос для обновления данных.
    """
    with DBContextManager() as cursor:
        cursor.execute(query, params)
