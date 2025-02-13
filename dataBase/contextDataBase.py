import sqlite3
from functions.functions import db_ops

#Доработать

class ContextDataBase:
    def __init__(self, path:str):
        """
        Инициализирует объект базы данных контекста.

        :param path: Путь к файлу базы данных.
        """
        self.path = path
        self._createTables()
    
    def _createTables(self):
        """
        Создает таблицу Context, если она не существует.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Context(
                    chat TEXT PRIMARY KEY,
                    context TEXT NOT NULL
                    )
                    '''
                    )
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
    

    def updateContext(self, chat:str, context:str) -> None:
        """
        Обновляет контекст для указанного чата.

        :param chat: Идентификатор чата.
        :param context: Новый контекст.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("UPDATE Context SET context = ? WHERE chat = ?", [context, chat])
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении контекста: {e}")
    
    def getContext(self, chat:str) -> str:
        """
        Возвращает контекст для указанного чата.

        :param chat: Идентификатор чата.
        :return: Контекст чата.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT context FROM Context WHERE chat = ?", [chat])
                context = cursor.fetchone()
                if context:
                    return list(context[0])
                else:
                    return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении контекста: {e}")

    def findContext(self, chat:str) -> bool:
        """
        Проверяет, существует ли контекст для указанного чата.

        :param chat: Идентификатор чата.
        :return: True, если контекст существует, иначе False.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT * FROM Context WHERE chat = ?", [chat])
                context = cursor.fetchone()
                if context:
                    return True
                else:
                    return False
        except sqlite3.Error as e:
            print(f"Ошибка при поиске контекста: {e}")

    def insertContext(self, chat:str, context:str) -> None:
        """
        Вставляет новый контекст для указанного чата.

        :param chat: Идентификатор чата.
        :param context: Контекст чата.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("INSERT INTO Context (chat, context) VALUES (?,?)", [chat, context])
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении контекста: {e}")

   
    


    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Выполняет действия при выходе из контекстного менеджера.
        """
        pass

