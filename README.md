# Диаграмма взаимодействия классов

![Взаимодействие классов](https://cdn.imgpile.com/f/sfgcrxT_xl.png)

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

# Техническая документация

## DataBase.py

### Описание

Этот файл содержит класс для работы с локальной базой данных SQLite. Основной класс:

- `DataBase`: Класс для управления базой данных.

### Классы и методы

#### DataBase

- `__init__(self, path: str)`: Инициализация класса и создание необходимых таблиц.
- `_createTables(self)`: Создание таблиц в базе данных.
- `addDataInTableGroupOccupancy(self) -> None`: Добавление данных в таблицу GroupOccupancy на основе данных из таблицы RegularLessons.
- `synchroniseTableRegularLessons(self, groups: list[dict[str: any]]) -> None`: Синхронизация таблицы RegularLessons с предоставленными данными.
- `insertNewLocation(self, data: dict) -> None`: Вставка новой локации в таблицу Locations, если запись с таким ID не существует.
- `synchroniseTeachers(self, data: dict) -> None`: Синхронизация таблицы Teachers с предоставленными данными.
- `fillTableStudentAbsences(self, students: list) -> None`: Заполнение таблицы StudentAbsences данными об отсутствии студентов.
- `getRegularLessonsIds(self) -> list[int]`: Получение списка идентификаторов всех регулярных занятий.
- `_selectData(self, tableName: str, field: str = None, param = None) -> list[tuple]`: Выполнение SELECT запроса к базе данных.
- `_formatLocationsOrTeachers(self, data: list[tuple]) -> list[dict[str: any]]`: Форматирование данных о локациях или преподавателях.
- `_formatLocationOrTeacher(self, data: tuple) -> dict[str: any]`: Форматирование данных о локации или преподавателе.
- `_formatGroupsOccupancyData(self, groups: list) -> list[dict[str: any]]`: Форматирование данных о заполненности групп.
- `_formatGroupOccupancyData(self, group: tuple) -> dict[str: any]`: Форматирование данных о заполненности группы.
- `_fromatRegularLessons(self, lessons: list[tuple]) -> list[dict[str: any]]`: Форматирование данных о регулярных занятиях.
- `_formatRegularLesson(self, lesson: tuple) -> dict[str: any]`: Форматирование данных о регулярном занятии.
- `_formatStudentAbsences(self, students: list[tuple]) -> list[dict[str: any]]`: Форматирование данных об отсутствии студентов.
- `_formatStudentStudentAbsences(self, student: tuple) -> dict[str: any]`: Форматирование данных об отсутствии студента.
- `getAllGroupsOccupancy(self) -> str`: Возвращает строку с информацией о заполненности всех групп.

### Форматирование данных

#### `_formatLocationsOrTeachers`

Возвращает список словарей с отформатированными данными о локациях или преподавателях. Поля:

- `id`: Идентификатор.
- `name`: Имя.

#### `_formatGroupOccupancyData`

Возвращает словарь с отформатированными данными о заполненности группы. Поля:

- `idGroup`: Идентификатор группы.
- `newStudents`: Новые студенты.
- `idsStudents`: Идентификаторы студентов.
- `dateOfEvent`: Дата события.
- `count`: Количество.
- `lastUpdate`: Последнее обновление.

#### `_formatRegularLesson`

Возвращает словарь с отформатированными данными о регулярном занятии. Поля:

- `id`: Идентификатор.
- `topic`: Тема.
- `idsStudents`: Идентификаторы студентов.
- `location`: Локация.
- `teacher`: Преподаватель.
- `day`: День.
- `timeFrom`: Время начала.
- `timeTo`: Время окончания.
- `assignWorkOffs`: Назначение отработок.
- `maxStudents`: Максимальное количество студентов.
- `lastUpdate`: Последнее обновление.

#### `_formatStudentAbsences`

Возвращает список словарей с отформатированными данными об отсутствии студентов. Поля:

- `idStudent`: Идентификатор студента.
- `name`: Имя.
- `date`: Дата.
- `topic`: Тема.
- `idGroup`: Идентификатор группы.
- `idLesson`: Идентификатор урока.
- `phoneNumber`: Номер телефона.
- `teacher`: Преподаватель.
- `workOffScheduled`: Запланированная отработка.
- `dateNextConnection`: Дата следующего соединения.
- `dateLastConnection`: Дата последнего соединения.
- `groupForWorkingOut`: Группа для отработки.

### Примечания

- Убедитесь, что у вас есть доступ к API AlfaCRM и необходимые учетные данные.
- Настройте параметры обновления в соответствии с вашими требованиями.
- Используйте методы классов для получения и синхронизации данных с CRM-системой и локальной базой данных.



### Баги

 - Метод getRegularLessonsByLocationId класса AlfaCRMDataManager. Если урок не проведён, выдаёт ошибку. Нужно выдавать сообщение пользователю о том, что нужно провести урок. 

 -Прерывается подключение к AlfaCRM, происходит 1 раз из 10, подумать над решением
