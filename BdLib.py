import sqlite3
import texts
class DatabaseMeta(type):
    def __new__(cls, name, bases, attrs):
            # Создание атрибута 'db' в классе
        attrs['db'] = sqlite3.connect(texts.database, check_same_thread=False)
        attrs['cursor'] = attrs['db'].cursor()
        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=DatabaseMeta):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self):
        attrs = [attr for attr in self.__dict__ if not attr.startswith('__')]
        attrs_values = [(attr, getattr(self, attr)) for attr in attrs if not callable(getattr(self, attr)) and attr!='cursor' and attr!="table_name"]
        # Формирование SQL-запроса INSERT
        table_name = self.__class__.__name__
        columns = '=? and '.join([attr for attr, value in attrs_values])+"=?"
        query = f"SELECT * FROM {table_name} WHERE {columns} "
        values = [value for attr, value in attrs_values]
        self.cursor.execute(query,(values))
        rows = self.cursor.fetchone()
        i=0
        if rows == None:
            return None
        for attr in self.__class__.__dict__:
            if not attr.startswith('__') and attr!='cursor' and attr!="table_name" and not callable(getattr(self, attr)):
                setattr(self, attr, rows[i])
                i+=1
        return self
    def insert(self):
        # Получение списка атрибутов и значений объекта модели
        attrs = [attr for attr in self.__dict__ if not attr.startswith('__')]
        attrs_values = [(attr, getattr(self, attr)) for attr in attrs if not callable(getattr(self, attr)) and attr!='cursor' and attr!="table_name"]
        # Формирование SQL-запроса INSERT
        table_name = self.__class__.__name__
        columns = ', '.join([attr for attr, value in attrs_values])
        placeholders = ', '.join(['?' for _ in attrs_values])
        values = [value for attr, value in attrs_values]
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.db.commit()
    def update(self):
        # Получение списка атрибутов и значений объекта модели
        attrs = [attr for attr in self.__dict__ if not attr.startswith('__')]
        attrs_values = [(attr, getattr(self, attr)) for attr in attrs if not callable(getattr(self, attr)) and attr!='cursor' and attr!="table_name"]
        # Формирование SQL-запроса INSERT
        table_name = self.__class__.__name__
        columns = '=?, '.join([attr for attr, value in attrs_values[1:]])+"=?"
        first = attrs_values[0][0]+"=?"
        values = [value for attr, value in attrs_values[1:]]
        values.append(attrs_values[0][1])
        query = f"UPDATE {table_name} SET {columns} WHERE {first}"
        # Выполнение SQL-запроса
        self.cursor.execute(query, values)
        self.db.commit()
    def delete(self):
        attrs = [attr for attr in self.__dict__ if not attr.startswith('__')]
        attrs_values = [(attr, getattr(self, attr)) for attr in attrs if not callable(getattr(self, attr)) and attr!='cursor' and attr!="table_name"]
        # Формирование SQL-запроса INSERT
        table_name = self.__class__.__name__
        columns = '=? and '.join([attr for attr, value in attrs_values])+"=?"
        query = f"DELETE FROM {table_name} WHERE {columns} "
        values = [value for attr, value in attrs_values]
        print(query)
        self.cursor.execute(query,(values))
    def fetch_all(self):
        # Формирование SQL-запроса SELECT
        table_name = self.__class__.__name__
        query = f"SELECT * FROM {table_name}"
        # Выполнение SQL-запроса
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # Создание экземпляров модели для каждой строки
        models = []
        for row in rows:
            model = self.__class__()
            
            i=0
            for attr in self.__class__.__dict__:
                if not attr.startswith('__') and attr!='cursor' and attr!="table_name"  and not callable(getattr(self, attr)):
                    setattr(model, attr, row[i])
                    i+=1
            models.append(model)
        return models


class Server(Model):
    id=0
    url=""
    sha256=""
    country=""
s=Server().fetch_all()






"""
class Category(Model):
    table_name = 'Category'

# Пример использования

# Создаем объекты моделей
category = Category(name='Electronics')
tovar = Tovar(name='Smartphone', id=5)

# Сохраняем объекты в базе данных
category.save()
tovar.save()
# Получаем все объекты модели Tovar из базы данных
tovars = Tovar().fetch_all()
for t in tovars:
    print(t.name)

# Закрываем соединение с базой данных
del Category
del Tovar
"""