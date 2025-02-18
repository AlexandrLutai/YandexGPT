import aiosqlite
from functions.functions import db_ops

class DatabaseManager:
    """
    Класс для управления базой данных.
    """

    def __init__(self, path: str):
        """
        Инициализирует объект DatabaseManager.

        Args:
            path (str): Путь к файлу базы данных.
        """
        self.path = path
        self._create_tables()

    async def _create_tables(self):
        """
        Создаёт необходимые таблицы в базе данных.
        """
        try:
            async with db_ops(self.path) as cursor:
                await cursor.executescript(
                    '''
                    CREATE TABLE IF NOT EXISTS StudentAbsences(
                    idStudent INTEGER NOT NULL, 
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    idGroup TEXT NOT NULL,
                    idLesson INTEGER NOT NULL,
                    phoneNumber TEXT NOT NULL,
                    teacher INTEGER NOT NULL,
                    workOffScheduled INTEGER NOT NULL DEFAULT 0,
                    dateNextConnection TEXT DEFAULT 0,
                    dateLastConnection TEXT,
                    groupForWorkingOut INTEGER,
                    dateAdded TEXT DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS GroupOccupancy(
                    idGroup INTEGER,
                    newStudents TEXT,
                    idsStudents TEXT,
                    dateOfEvent TEXT,
                    count INTEGER DEFAULT 0,
                    lastUpdate TEXT,
                    worksOffsTopics TEXT
                    );
                    CREATE TABLE IF NOT EXISTS RegularLessons(
                    idGroup INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    idsStudents TEXT,
                    location INTEGER NOT NULL,
                    teacher INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    timeFrom TEXT NOT NULL,
                    timeTo TEXT NOT NULL,
                    assignWorkOffs INTEGER DEFAULT 1,
                    maxStudents INTEGER NOT NULL,
                    lastUpdate TEXT NOT NULL,
                    subjectId INTEGER 
                    );
                    CREATE TABLE IF NOT EXISTS Locations(
                    id INTEGER NOT NULL,
                    name TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS Teachers(
                    id INTEGER NOT NULL,
                    name TEXT NOT NULL
                    )
                    '''
                )
        except aiosqlite.Error as e:
            print(f"Ошибка при создании таблиц: {e}")

    async def insert_data(self, table: str, data: dict) -> None:
        """
        Вставляет данные в указанную таблицу.

        Args:
            table (str): Название таблицы.
            data (dict): Словарь с данными для вставки.
        """
        if not data:
            return
        keys = data.keys()
        placeholders = ','.join(['?' for i in range(len(data))])
        colums = ','.join(keys)
        try:
            async with db_ops(self.path) as cursor:
                await cursor.execute(f"INSERT INTO {table} ({colums}) VALUES ({placeholders})", tuple(data.values()))
        except aiosqlite.Error as e:
            print(f"Ошибка при вставке данных: {e}")

    async def insert_a_lot_of_unique_data(self, table: str, data: list[dict], selectedFields: list[str]) -> None:
        """
        Вставляет множество уникальных записей в указанную таблицу.

        Args:
            table (str): Название таблицы.
            data (list[dict]): Список словарей с данными для вставки.
            selectedFields (list[str]): Список полей для проверки уникальности.
        """
        if not data or not selectedFields:
            return
        for item in data:
            await self.insert_unique_data(table, item, {key: item[key] for key in selectedFields})

    async def insert_a_lot_of_data(self, table: str, data: list[dict]) -> None:
        """
        Вставляет множество записей в указанную таблицу.

        Args:
            table (str): Название таблицы.
            data (list[dict]): Список словарей с данными для вставки.
        """
        if not data:
            return
        for item in data:
            await self.insert_data(table, item)

    async def insert_unique_data(self, table: str, data: dict, selectedParams: dict) -> None:
        """
        Вставляет уникальные данные в указанную таблицу.

        Args:
            table (str): Название таблицы.
            data (dict): Словарь с данными для вставки.
            selectedParams (dict): Словарь с параметрами для проверки уникальности.
        """
        if not data or not selectedParams:
            return
        sql = f"SELECT * FROM {table} WHERE " + " AND ".join([f"{key} = ?" for key in selectedParams.keys()])
        try:
            async with db_ops(self.path) as cursor:
                await cursor.execute(sql, tuple(selectedParams.values()))
                if not await cursor.fetchone():
                    await self.insert_data(table, data)
        except aiosqlite.Error as e:
            print(f"Ошибка при вставке уникальных данных: {e}")

    async def clear_table(self, table: str) -> None:
        """
        Очищает указанную таблицу.

        Args:
            table (str): Название таблицы.
        """
        try:
            async with db_ops(self.path) as cursor:
                await cursor.execute(f"DELETE FROM {table}")
        except aiosqlite.Error as e:
            print(f"Ошибка при очистке таблицы: {e}")

    async def _select_data(self, table: str, getAllData: bool = True, selectedParams: dict = None) -> tuple:
        """
        Выбирает данные из указанной таблицы.

        Args:
            table (str): Название таблицы.
            getAllData (bool): Флаг для выбора всех данных или одной записи.
            selectedParams (dict, optional): Словарь с параметрами для условия WHERE.

        Returns:
            tuple: Кортеж с выбранными данными. | list[tuple]: Список кортежей с выбранными данными.
        """
        if not selectedParams:
            sql = f"SELECT * FROM {table}"
            params = ()
        else:
            sql = f"SELECT * FROM {table} WHERE " + " AND ".join([f"{key} = ?" for key in selectedParams.keys()])
            params = tuple(selectedParams.values())
        try:
            async with db_ops(self.path) as cursor:
                await cursor.execute(sql, params)
                if getAllData:
                    return await cursor.fetchall()
                else:
                    return await cursor.fetchone()
        except aiosqlite.Error as e:
            print(f"Ошибка при выборке данных: {e}")
            return ()

    async def select_all_data(self, table: str, selectedParams: dict = None) -> list[tuple]:
        """
        Выбирает все данные из указанной таблицы.

        Args:
            table (str): Название таблицы.
            selectedParams (dict, optional): Словарь с параметрами для условия WHERE.

        Returns:
            list[tuple]: Список кортежей с выбранными данными.
        """
        return await self._select_data(table, True, selectedParams)

    async def select_one_data(self, table: str, selectedParams: dict = None) -> tuple:
        """
        Выбирает одну запись из указанной таблицы.

        Args:
            table (str): Название таблицы.
            selectedParams (dict, optional): Словарь с параметрами для условия WHERE.

        Returns:
            tuple: Кортеж с выбранными данными.
        """
        return await self._select_data(table, False, selectedParams)

    async def update_data(self, data: dict[str, any], tableName: str, selectPams: dict[str, any] | None) -> None:
        """
        Обновляет данные в указанной таблице.

        Args:
            data (dict[str, any]): Словарь с данными для обновления.
            tableName (str): Название таблицы.
            selectPams (dict[str, any] | None): Словарь с параметрами для условия WHERE.
        """
        try:
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            params = list(data.values())

            if selectPams:
                where_clause = " AND ".join([f"{key} = ?" for key in selectPams.keys()])
                params.extend(selectPams.values())
                sql = f"UPDATE {tableName} SET {set_clause} WHERE {where_clause}"
            else:
                sql = f"UPDATE {tableName} SET {set_clause}"

            async with db_ops(self.path) as cursor:
                await cursor.execute(sql, params)
        except aiosqlite.Error as e:
            print(f"Ошибка при обновлении данных в таблице {tableName}: {e}")

    async def delete_data(self, table: str, selectedParams: dict = None) -> None:
        """
        Удаляет данные из указанной таблицы.

        Args:
            table (str): Название таблицы.
            selectedParams (dict, optional): Словарь с параметрами для условия WHERE.
        """
        if not selectedParams:
            sql = f"DELETE FROM {table}"
            param = ()
        else:
            sql = f"DELETE FROM {table} WHERE " + " AND ".join([f"{key} = ?" for key in selectedParams.keys()])
            param = tuple(selectedParams.values())
        try:
            async with db_ops(self.path) as cursor:
                await cursor.execute(sql, param)
        except aiosqlite.Error as e:
            print(f"Ошибка при удалении данных: {e}")

    async def delete_a_lot_of_data(self, table: str, data: list[dict]) -> None:
        """
        Удаляет множество записей из указанной таблицы.

        Args:
            table (str): Название таблицы.
            data (list[dict]): Список словарей с параметрами для удаления.
        """
        if not data:
            return
        for item in data:
            await self.delete_data(table, item)
