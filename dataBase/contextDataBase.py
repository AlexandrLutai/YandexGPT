import aiosqlite

class ContextDataBase:
    def __init__(self, path: str):
        """
        Инициализирует объект базы данных контекста.

        :param path: Путь к файлу базы данных.
        """
        self.path = path

    async def _createTables(self):
        """
        Создает таблицу Context, если она не существует.
        """
        try:
            async with aiosqlite.connect(self.path) as db:
                await db.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Context(
                    chat TEXT PRIMARY KEY,
                    context TEXT NOT NULL
                    )
                    '''
                )
                await db.commit()
        except aiosqlite.Error as e:
            print(f"Ошибка при создании таблиц: {e}")

    async def updateContext(self, chat: str, context: str) -> None:
        """
        Обновляет контекст для указанного чата.

        :param chat: Идентификатор чата.
        :param context: Новый контекст.
        """
        try:
            async with aiosqlite.connect(self.path) as db:
                await db.execute("UPDATE Context SET context = ? WHERE chat = ?", [context, chat])
                await db.commit()
        except aiosqlite.Error as e:
            print(f"Ошибка при обновлении контекста: {e}")

    async def getContext(self, chat: str) -> str:
        """
        Возвращает контекст для указанного чата.

        :param chat: Идентификатор чата.
        :return: Контекст чата.
        """
        try:
            async with aiosqlite.connect(self.path) as db:
                async with db.execute("SELECT context FROM Context WHERE chat = ?", [chat]) as cursor:
                    context = await cursor.fetchone()
                    if context:
                        return list(context[0])
                    else:
                        return None
        except aiosqlite.Error as e:
            print(f"Ошибка при получении контекста: {e}")

    async def findContext(self, chat: str) -> bool:
        """
        Проверяет, существует ли контекст для указанного чата.

        :param chat: Идентификатор чата.
        :return: True, если контекст существует, иначе False.
        """
        try:
            async with aiosqlite.connect(self.path) as db:
                async with db.execute("SELECT * FROM Context WHERE chat = ?", [chat]) as cursor:
                    context = await cursor.fetchone()
                    if context:
                        return True
                    else:
                        return False
        except aiosqlite.Error as e:
            print(f"Ошибка при поиске контекста: {e}")

    async def insertContext(self, chat: str, context: str) -> None:
        """
        Вставляет новый контекст для указанного чата.

        :param chat: Идентификатор чата.
        :param context: Контекст чата.
        """
        try:
            async with aiosqlite.connect(self.path) as db:
                await db.execute("INSERT INTO Context (chat, context) VALUES (?,?)", [chat, context])
                await db.commit()
        except aiosqlite.Error as e:
            print(f"Ошибка при добавлении контекста: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Выполняет действия при выходе из контекстного менеджера.
        """
        pass

