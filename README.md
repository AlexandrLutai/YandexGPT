# Техническая документация

## alfaCRM.py

### Описание

Этот файл содержит классы для работы с CRM-системой AlfaCRM. Основные классы:

- `AlfaCRM`: Класс для взаимодействия с API AlfaCRM.
- `AlfaCRMDataManager`: Класс для управления данными, полученными из AlfaCRM.
- `AlfaCRMDBManager`: Класс для синхронизации данных с локальной базой данных.

### Классы и методы

#### AlfaCRM

- `__init__(self, hostname: str, email: str, key: str)`: Инициализация класса с указанием хоста, email и ключа API.
- `_getTempToken(self) -> str`: Получение временного токена для доступа к API.
- `_fillHeader(self) -> None`: Заполнение заголовка запроса с временным токеном.
- `_getBrunches(self) -> int`: Получение идентификатора филиала.
- `_getIdBrunches(self, brunches: list) -> int`: Получение идентификатора филиала из списка филиалов.
- `getData(self, model: str, data: dict) -> list`: Получение данных из указанной модели.

#### AlfaCRMDataManager

- `__init__(self, crm: AlfaCRM, updatePeriotByNexLesson: int = 7, updatePeriodByPrevLesson: int = 7)`: Инициализация класса с указанием CRM и периодов обновления.
- `_getRegularLessons(self, allLessons: list) -> list`: Получение регулярных уроков из списка всех уроков.
- `_getNextLessonsByLocation(self, locationId: int) -> list`: Получение следующих уроков по идентификатору локации.
- `_getPreviusLessonByGroupId(self, groupId: int) -> list`: Получение предыдущих уроков по идентификатору группы.
- `getLocations(self) -> list`: Получение списка локаций.
- `_formatLocationsData(self, locations: list) -> list`: Форматирование данных локаций.
- `getRegularLessonsByLocationId(self, locationId: int) -> list`: Получение регулярных уроков по идентификатору локации.
- `_getGroupById(self, groupId: int) -> list`: Получение группы по идентификатору.
- `getTeachers(self) -> list`: Получение списка учителей.
- `_formatTeachersData(self, data: list)`: Форматирование данных учителей.
- `getStudentsMissedLesson(self, groupId: int) -> list`: Получение списка студентов, пропустивших урок.
- `_getStudents(self) -> list`: Получение списка студентов.
- `_findStudent(self, table: list, key: str, value)`: Поиск студента в таблице.
- `_fillTempLists(self)`: Заполнение временных списков.
- `_clearTempLists(self)`: Очистка временных списков.
- `synchronizeGroupOccupancyTable(self, synchronizeAnyware: bool = False)`: Синхронизация таблицы заполняемости групп.
- `addStudentInTableStudentAsences(self)`: Добавление студента в таблицу отсутствий.
- `_fillTableStudentAsences(self)`: Заполнение таблицы отсутствий студентов.

#### AlfaCRMDBManager

- `__init__(self, dataBase: DataBase, alfaCRMDataManager: AlfaCRMDataManager)`: Инициализация класса с указанием базы данных и менеджера данных AlfaCRM.
- `synchroniseTeachers(self)`: Синхронизация учителей.
- `synchroniseRegularLessons(self)`: Синхронизация регулярных уроков.
- `insertInStudentAbsences(self)`: Вставка данных об отсутствующих студентах.

### Примечания

- Убедитесь, что у вас есть доступ к API AlfaCRM и необходимые учетные данные.
- Настройте параметры обновления в соответствии с вашими требованиями.
- Используйте методы классов для получения и синхронизации данных с CRM-системой и локальной базой данных.