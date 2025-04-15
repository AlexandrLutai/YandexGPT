
# Диаграмма взаимодействия классов

![Взаимодействие классов](https://imgur.com/a/l5YVZJx)

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

`AlfaCRMDataManager` - это класс, который реализует интерфейс `CrmDataManagerInterface` и отвечает за форматирование данных при добавлении и получении информации из CRM.

### Атрибуты

- `crm (AlfaCRM)` - Экземпляр класса AlfaCRM.
- `workOffType (AlfaCRMDataManager.WorkOffType)` - Тип отработки.
- `updatePeriodToNextLesson (int)` - Период обновления до следующего урока.
- `updatePeriodToPreviousLesson (int)` - Период обновления до предыдущего урока.

### Методы

- `get_locations() -> List[LocationDict]`
  - Получает список локаций.
  - Возвращает: `List[LocationDict]` - Список локаций.

- `get_regular_lessons_by_location_id(locationId: int) -> List[RegularLessonDict]`
  - Получает регулярные уроки по идентификатору локации.
  - Аргументы:
    - `locationId (int)` - Идентификатор локации.
  - Возвращает: `List[RegularLessonDict]` - Список регулярных уроков.

- `get_teachers() -> List[Dict[str, str]]`
  - Получает список учителей.
  - Возвращает: `List[Dict[str, str]]` - Список учителей.

- `get_students_missed_lesson(groupId: int) -> List[StudentAbsenceDict]`
  - Получает список студентов, пропустивших урок.
  - Аргументы:
    - `groupId (int)` - Идентификатор группы.
  - Возвращает: `List[StudentAbsenceDict]` - Список студентов, пропустивших урок.

- `add_work_off(data: CreateLessonModelDict) -> None`
  - Добавляет отработку урока.
  - Аргументы:
    - `data (CreateLessonModelDict)` - Данные урока.


## AlfaCRM

`AlfaCRM` - это класс для взаимодействия с API AlfaCRM.

### Атрибуты

- `MODELS_FOR_GETTING_DATA (dict)` - Константный словарь, содержащий пути для получения данных из различных моделей.
- `MODELS_FOR_CREATING (dict)` - Константный словарь, содержащий пути для создания новых записей в различных моделях.

### Методы

- `__init__(hostname: str, email: str, key: str)`
  - Инициализирует объект AlfaCRM.
  - Аргументы:
    - `hostname (str)` - Имя хоста в CRM.
    - `email (str)` - Электронная почта для авторизации.
    - `key (str)` - API ключ для авторизации.

- `_get_temp_token() -> str`
  - Получает временный токен для авторизации.
  - Возвращает: `str` - Временный токен.

- `_fill_header() -> None`
  - Заполняет заголовок запроса временным токеном.

- `_get_brunches() -> requests.Response`
  - Получает данные филиалов.
  - Возвращает: `requests.Response` - Ответ от сервера.

- `_get_id_brunches(brunches: list[int]) -> int`
  - Получает идентификатор филиала из списка филиалов.
  - Аргументы:
    - `brunches (list[int])` - Список филиалов.
  - Возвращает: `int` - Идентификатор филиала.

- `create_model(model: str, data: dict[str, any]) -> requests.Response`
  - Создает модель в CRM.
  - Аргументы:
    - `model (str)` - Название модели. Ключ словаря MODELS_FOR_CREATING.
    - `data (dict[str, any])` - Данные для создания модели.
  - Возвращает: `requests.Response` - Ответ от сервера.

- `get_data(model: str, data: dict[str, any]) -> requests.Response`
  - Получает данные из CRM.
  - Аргументы:
    - `model (str)` - Название модели. Ключ словаря MODELS_FOR_GETTING_DATA.
    - `data (dict[str, any])` - Данные для запроса.
  - Возвращает: `requests.Response` - Ответ от сервера.

- `get_items(response: requests.Response) -> dict[str, any]`
  - Получает список данных из ответа.
  - Аргументы:
    - `response (requests.Response)` - Ответ от сервера.
  - Возвращает: `dict[str, any]` - Список данных.


## AlfaCRMDBManager

`AlfaCRMDBManager` - это класс, который добавляет данные из CRM в базу данных.

### Атрибуты

- `dataBase (DataBase)` - Экземпляр класса DataBase.
- `alfaCRMDataManager (AlfaCRMDataManager)` - Экземпляр класса AlfaCRMDataManager.

### Методы

- `__init__(dataBase: DataBase, alfaCRMDataManager: AlfaCRMDataManager)`
  - Инициализирует менеджер базы данных CRM.
  - Аргументы:
    - `dataBase (DataBase)` - Экземпляр класса DataBase.
    - `alfaCRMDataManager (AlfaCRMDataManager)` - Экземпляр класса AlfaCRMDataManager.

- `synchronise_teachers() -> None`
  - Синхронизирует данные учителей с базой данных.

- `synchronise_regular_lessons() -> None`
  - Синхронизирует регулярные уроки с базой данных.

- `insert_in_student_absences() -> None`
  - Вставляет данные о пропусках студентов в базу данных.


# Database module

## DataBase

`DataBase` - это класс, который создает необходимые таблицы и предоставляет интерфейс для работы с ними.

### Методы

- `__init__(path: str)`
  - Инициализирует объект базы данных.
  - Аргументы:
    - `path (str)` - Путь к файлу базы данных.

- `add_data_in_table_group_occupancy(synchroniseParams: list[int] | None = None) -> None`
  - Добавляет данные в таблицу GroupOccupancy.
  - Аргументы:
    - `synchroniseParams (list[int] | None)` - Параметры для синхронизации.

- `synchronise_table_regular_lessons(groups: list[RegularLessonDict]) -> None`
  - Синхронизирует таблицу RegularLessons с предоставленными данными.
  - Аргументы:
    - `groups (list[RegularLessonDict])` - Список словарей с данными о регулярных занятиях.

- `insert_new_location(data: LocationDict) -> None`
  - Вставляет новую запись в таблицу Locations.
  - Аргументы:
    - `data (LocationDict)` - Словарь с данными о локации.

- `synchronise_teachers(data: list[LocationDict]) -> None`
  - Синхронизирует таблицу Teachers с предоставленными данными.
  - Аргументы:
    - `data (list[LocationDict])` - Список словарей с данными о преподавателях.

- `fill_table_student_absences(students: list[StudentAbsenceDict]) -> None`
  - Заполняет таблицу StudentAbsences данными об отсутствии студентов.
  - Аргументы:
    - `students (list[StudentAbsenceDict])` - Список словарей с данными об отсутствии студентов.

- `get_regular_lessons_ids() -> list[int]`
  - Возвращает список идентификаторов регулярных занятий.
  - Возвращает: `list[int]` - Список идентификаторов регулярных занятий.

- `get_group_occupancy_data(idGroup: int) -> GroupOccupancyDict`
  - Возвращает данные о заполненности группы.
  - Аргументы:
    - `idGroup (int)` - Идентификатор группы.
  - Возвращает: `GroupOccupancyDict` - Словарь с данными о заполненности группы.

- `get_available_groups(idGroup: int = None, idLocation: str = None) -> str`
  - Возвращает строку с информацией о доступных группах.
  - Аргументы:
    - `idGroup (int, optional)` - Идентификатор группы для фильтрации. Defaults to None.
    - `idLocation (str, optional)` - Идентификатор локации для фильтрации. Defaults to None.
  - Возвращает: `str` - Строка с информацией о доступных группах.

- `get_students_absences_information() -> list[StudentAbsenceDict]`
  - Возвращает информацию об отсутствии студентов.
  - Возвращает: `list[StudentAbsenceDict]` - Список словарей с данными об отсутствии студентов.

- `get_regular_lessons(idGroup: int) -> RegularLessonDict`
  - Возвращает данные о регулярных занятиях для указанной группы.
  - Аргументы:
    - `idGroup (int)` - Идентификатор группы.
  - Возвращает: `RegularLessonDict` - Словарь с данными о регулярных занятиях.

- `get_student(phoneNumber: str) -> StudentAbsenceDict`
  - Возвращает данные о студенте по номеру телефона.
  - Аргументы:
    - `phoneNumber (str)` - Номер телефона студента.
  - Возвращает: `StudentAbsenceDict` - Словарь с данными о студенте.

- `get_all_locations() -> list[LocationDict]`
  - Возвращает список всех локаций.
  - Возвращает: `list[LocationDict]` - Список словарей с данными о локациях.


## DatabaseDataFormatter

`DatabaseDataFormatter` - это класс для форматирования данных из базы данных.

### Методы

- `format_group_occupancy_data(group: tuple) -> GroupOccupancyDict`
  - Форматирует данные о заполненности группы.
  - Аргументы:
    - `group (tuple)` - Кортеж с данными о заполненности группы.
  - Возвращает: `GroupOccupancyDict` - Словарь с отформатированными данными о заполненности группы.

- `format_groups_occupancy_data(groups: list[tuple]) -> list[GroupOccupancyDict]`
  - Форматирует данные о заполненности групп.
  - Аргументы:
    - `groups (list[tuple])` - Список кортежей с данными о заполненности групп.
  - Возвращает: `list[GroupOccupancyDict]` - Список словарей с отформатированными данными о заполненности групп.

- `format_locations_or_teachers(data: list[tuple]) -> list[LocationDict]`
  - Форматирует данные о локациях или преподавателях.
  - Аргументы:
    - `data (list[tuple])` - Список кортежей с данными о локациях или преподавателях.
  - Возвращает: `list[LocationDict]` - Список словарей с отформатированными данными.

- `format_location_or_teacher(data: tuple) -> LocationDict`
  - Форматирует данные о локации или преподавателе.
  - Аргументы:
    - `data (tuple)` - Кортеж с данными о локации или преподавателе.
  - Возвращает: `LocationDict` - Словарь с отформатированными данными.

- `fromat_regular_lessons(lessons: list[tuple]) -> list[RegularLessonDict]`
  - Форматирует данные о регулярных занятиях.
  - Аргументы:
    - `lessons (list[tuple])` - Список кортежей с данными о регулярных занятиях.
  - Возвращает: `list[RegularLessonDict]` - Список словарей с отформатированными данными о регулярных занятиях.

- `format_regular_lesson(lesson: tuple) -> RegularLessonDict`
  - Форматирует данные о регулярном занятии.
  - Аргументы:
    - `lesson (tuple)` - Кортеж с данными о регулярном занятии.
  - Возвращает: `RegularLessonDict` - Словарь с отформатированными данными о регулярном занятии.

- `format_students_absences(students: list[tuple]) -> list[StudentAbsenceDict]`
  - Форматирует данные об отсутствии студентов.
  - Аргументы:
    - `students (list[tuple])` - Список кортежей с данными об отсутствии студентов.
  - Возвращает: `list[StudentAbsenceDict]` - Список словарей с отформатированными данными об отсутствии студентов.

- `format_student_absence(student: tuple) -> StudentAbsenceDict`
  - Форматирует данные об отсутствии студента.
  - Аргументы:
    - `student (tuple)` - Кортеж с данными об отсутствии студента.
  - Возвращает: `StudentAbsenceDict` - Словарь с отформатированными данными об отсутствии студента.


## DatabaseManager

`DatabaseManager` - это класс для управления базой данных.

### Методы

- `__init__(path: str)`
  - Инициализирует объект DatabaseManager.
  - Аргументы:
    - `path (str)` - Путь к файлу базы данных.

- `_create_tables() -> None`
  - Создаёт необходимые таблицы в базе данных.

- `insert_data(table: str, data: dict) -> None`
  - Вставляет данные в указанную таблицу.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `data (dict)` - Словарь с данными для вставки.

- `insert_a_lot_of_unique_data(table: str, data: list[dict], selectedFields: list[str]) -> None`
  - Вставляет множество уникальных записей в указанную таблицу.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `data (list[dict])` - Список словарей с данными для вставки.
    - `selectedFields (list[str])` - Список полей для проверки уникальности.

- `insert_a_lot_of_data(table: str, data: list[dict]) -> None`
  - Вставляет множество записей в указанную таблицу.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `data (list[dict])` - Список словарей с данными для вставки.

- `insert_unique_data(table: str, data: dict, selectedParams: dict) -> None`
  - Вставляет уникальные данные в указанную таблицу.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `data (dict)` - Словарь с данными для вставки.
    - `selectedParams (dict)` - Словарь с параметрами для проверки уникальности.

- `clear_table(table: str) -> None`
  - Очищает указанную таблицу.
  - Аргументы:
    - `table (str)` - Название таблицы.

- `_select_data(table: str, getAllData: bool = True, selectedParams: dict = None) -> tuple | list[tuple]`
  - Выбирает данные из указанной таблицы.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `getAllData (bool)` - Флаг для выбора всех данных или одной записи.
    - `selectedParams (dict, optional)` - Словарь с параметрами для условия WHERE.
  - Возвращает: `tuple` - Кортеж с выбранными данными или `list[tuple]` - Список кортежей с выбранными данными.

- `select_all_data(table: str, selectedParams: dict = None) -> list[tuple]`
  - Выбирает все данные из указанной таблицы.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `selectedParams (dict, optional)` - Словарь с параметрами для условия WHERE.
  - Возвращает: `list[tuple]` - Список кортежей с выбранными данными.

- `select_one_data(table: str, selectedParams: dict = None) -> tuple`
  - Выбирает одну запись из указанной таблицы.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `selectedParams (dict, optional)` - Словарь с параметрами для условия WHERE.
  - Возвращает: `tuple` - Кортеж с выбранными данными.

- `update_data(data: dict[str, any], tableName: str, selectPams: dict[str, any] | None) -> None`
  - Обновляет данные в указанной таблице.
  - Аргументы:
    - `data (dict[str, any])` - Словарь с данными для обновления.
    - `tableName (str)` - Название таблицы.
    - `selectPams (dict[str, any] | None)` - Словарь с параметрами для условия WHERE.

- `delete_data(table: str, selectedParams: dict = None) -> None`
  - Удаляет данные из указанной таблицы.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `selectedParams (dict, optional)` - Словарь с параметрами для условия WHERE.

- `delete_a_lot_of_data(table: str, data: list[dict]) -> None`
  - Удаляет множество записей из указанной таблицы.
  - Аргументы:
    - `table (str)` - Название таблицы.
    - `data (list[dict])` - Список словарей с параметрами для удаления.

# GPT module

## YandexGPTModel

`YandexGPTModel` - это класс для взаимодействия с моделью YandexGPT.

### Методы

- `__init__(authKey: str, cloudBranch: str, temperature: float = 0.3)`
  - Инициализирует объект модели YandexGPT.
  - Аргументы:
    - `authKey (str)` - Ключ авторизации для API.
    - `cloudBranch (str)` - Ветка облака для модели.
    - `temperature (float)` - Температура генерации текста. По умолчанию 0.3.

- `_fill_GPT_prompt(messages: list[MessageForPromptDict]) -> dict`
  - Заполняет запрос для модели GPT.
  - Аргументы:
    - `messages (list[MessageForPromptDict])` - Список сообщений.
  - Возвращает: `dict` - Заполненный запрос.

- `request(messages: list[MessageForPromptDict]) -> str`
  - Отправляет запрос к модели GPT.
  - Аргументы:
    - `messages (list[MessageForPromptDict])` - Список сообщений.
  - Возвращает: `str` - Ответ модели.

## YandexGPTChatBot

`YandexGPTChatBot` - это класс для взаимодействия с моделью YandexGPT через чат-бот.

### Атрибуты

- `_gpt (YandexGPTModel)` - Экземпляр модели YandexGPT.
- `_db (DataBase)` - Экземпляр базы данных.
- `_contextDB (ContextDataBase)` - Контекстная база данных.
- `_currentContext (dict[str, list[dict[str: str]]])` - Текущий контекст чатов.
- `_groups (list)` - Список групп.
- `students (list)` - Список студентов.
- `_currentMessages (dict)` - Текущие сообщения.
- `messageAnalyzer (MessageAnalyzer)` - Анализатор сообщений.

### Методы

- `__init__(gpt: YandexGPTModel, db: DataBase, crm: CrmDataManagerInterface, contextDB: ContextDataBase)`
  - Инициализирует объект чат-бота YandexGPT.
  - Аргументы:
    - `gpt (YandexGPTModel)` - Экземпляр модели YandexGPT.
    - `db (DataBase)` - Экземпляр базы данных.
    - `crm (CrmDataManagerInterface)` - Интерфейс менеджера данных CRM.
    - `contextDB (ContextDataBase)` - Контекстная база данных.

- `_get_context(chatId: str) -> list[MessageForPromptDict]`
  - Получает контекст чата по идентификатору чата.
  - Аргументы:
    - `chatId (str)` - Идентификатор чата.
  - Возвращает: `list[MessageForPromptDict]` - Список сообщений контекста.

- `_del_from_current_context(chatId: str) -> None`
  - Удаляет контекст чата из текущего контекста.
  - Аргументы:
    - `chatId (str)` - Идентификатор чата.

- `_add_to_context(chat: str, role: str, message: str) -> None`
  - Добавляет сообщение в контекст чата.
  - Аргументы:
    - `chat (str)` - Идентификатор чата.
    - `role (str)` - Роль отправителя сообщения.
    - `message (str)` - Текст сообщения.

- `_get_message(scriptKey: str, chat: str, message: dict = None) -> list[MessageForPromptDict]`
  - Получает сообщение для отправки в модель GPT.
  - Аргументы:
    - `scriptKey (str)` - Ключ сценария.
    - `chat (str)` - Идентификатор чата.
    - `message (dict, optional)` - Сообщение для отправки. Defaults to None.
  - Возвращает: `list[MessageForPromptDict]` - Список сообщений для отправки.

- `_get_scenaries(message: str) -> str`
  - Получает сценарий для обработки сообщения.
  - Аргументы:
    - `message (str)` - Текст сообщения.
  - Возвращает: `str` - Ответ сценария.

- `send_message(scriptKey: str, chat: str, message: str) -> str`
  - Отправляет сообщение в модель GPT и получает ответ.
  - Аргументы:
    - `scriptKey (str)` - Ключ сценария.
    - `chat (str)` - Идентификатор чата.
    - `message (str)` - Текст сообщения.
  - Возвращает: `str` - Ответ модели GPT.


## MessageAnalyzer

`MessageAnalyzer` - это класс для анализа сообщений, полученных от модели YandexGPT.

### Методы

- `__init__(chatAnalyzer: ChatScriptAnalyzer, db: DataBase, crm: CrmDataManagerInterface)`
  - Инициализирует объект анализатора сообщений.
  - Аргументы:
    - `chatAnalyzer (ChatScriptAnalyzer)` - Экземпляр анализатора сценариев.
    - `db (DataBase)` - Экземпляр базы данных.
    - `crm (CrmDataManagerInterface)` - Интерфейс менеджера данных CRM.

- `analyze_GPT_answer(data: MessageForAnalyzeDict) -> str`
  - Анализирует ответ модели GPT.
  - Аргументы:
    - `data (MessageForAnalyzeDict)` - Данные для анализа.
  - Возвращает: `str` - Сообщение после анализа.

- `_analyze_system_message(data: MessageForAnalyzeDict) -> str`
  - Анализирует системное сообщение.
  - Аргументы:
    - `data (MessageForAnalyzeDict)` - Данные для анализа.
  - Возвращает: `str` - Сообщение после анализа.

- `_process_work_off_message(data: MessageForAnalyzeDict) -> None`
  - Обрабатывает сообщение об отработке.
  - Аргументы:
    - `data (MessageForAnalyzeDict)` - Данные для анализа.

- `_work_off_success(data: MessageForAnalyzeDict) -> None`
  - Обрабатывает успешное сообщение об отработке.
  - Аргументы:
    - `data (MessageForAnalyzeDict)` - Данные сообщения, включающие идентификатор чата и текст сообщения.

- `_work_off_fail(data: MessageForAnalyzeDict) -> None`
  - Обрабатывает неудачное сообщение об отработке.
  - Аргументы:
    - `data (MessageForAnalyzeDict)` - Данные сообщения, включающие идентификатор чата и текст сообщения.


## ChatScriptAnalyzer

`ChatScriptAnalyzer` - это класс для анализа сообщений пользователя и отправки их в модель YandexGPT.

### Методы

- `__init__(gpt: YandexGPTModel, instractionsPath: str)`
  - Инициализирует объект анализатора сообщений пользователя.
  - Аргументы:
    - `gpt (YandexGPTModel)` - Экземпляр модели YandexGPT.
    - `instractionsPath (str)` - Путь к файлу инструкций.

- `_get_scenaries(instructionsData: dict) -> str`
  - Получает сценарии из данных инструкций.
  - Аргументы:
    - `instructionsData (dict)` - Данные инструкций.
  - Возвращает: `str` - Строка с возможными сценариями.

- `_get_prompt(message: str) -> list`
  - Получает запрос для модели GPT.
  - Аргументы:
    - `message (str)` - Сообщение пользователя.
  - Возвращает: `list` - Список сообщений для отправки в модель GPT.

- `analyze(message: str) -> str`
  - Анализирует сообщение пользователя и отправляет его в модель GPT.
  - Аргументы:
    - `message (str)` - Сообщение пользователя.
  - Возвращает: `str` - Ответ модели GPT.


# Примечание

## Общее

Необходимо реализовать возможность ассинхронной работы для всех существующих модулей. 
 
## Модуль DataBase

### ContextDataBase

Рассмотреть необходимость хранения контекста чатов статически.

### DataBase

Добавить возможность выбора вариантов работы системы между назначением одной отработки в месяц и отработкой всех пропущенных занятий.

## Модуль CRM

### CRMDataManager

- Добавить различные варианты добавления отработок в CRM. Как отдельный урок или добавление в состав существующей группы.

- Возможно лучше разделить данный класс на два: Класс для получения данных из CRM и класс для внесения изменений в CRM

## Модуль GPT

### GPTChatScriptAnalyzer
Добавить возможность определения сущности чата между клиентом и лидом.

Добавить возможность определения сценариев диалога для клиента. Должны быть реализованы следующие сценарии:

- Назначение отработки 
- Запись пропуска урока, при учёте, что клиент предупредил об этом заранее
- Ответы на часто задаваемые вопросы
- Ответы на вопросы, связанные с абонементом клиента

Добавить возможность определения сценариев для лида. Должны быть реализованы следующие сценарии:

- Ответы на часто задаваемые вопросы 
- Запись лида на пробный урок

### GPTMessageAnalyzer
1. Отработки:
    - Добавить обработку отказа от отработки
    - Добавить возможность переноса записи на определённый срок

### Промпты

Необходимо подобрать наиболее эффективные инструкции, которые не будут позволять GPT отходить от стандартного сценария ведения диалога.

### Дообучение модели

Рассмотреть возможность дообучения модели. Основной проблемой является то, что обращение к дообученной модели на 60% дороже. Необходимо проверить, насколько эффективнее дообученная модель будет справляться с поставленной задачей.

### Проблема взаимодействия модели и системы

Единственная возможность организовать взаимодействие между системой и чат-ботом - текстовые сообщения. Подобный формат взаимодействия делает практически неизбежными ситуации, при которых будут возникать ошибки из-за несоблюдения ботом формата системных сообщений. Правильно составленные инструкции могут минимизировать количество подобных ошибок, однако не устранят их полностью. 
Одним из вариантов устранения ошибок подобного типа является написание отдельного модуля, который будет анализировать ответы GPT. Можно построить данный модуль на основе модели того же или более совершенного типа, такой подход будет увеличивать цену одного сообщения. 

### Проблема спам-запросов

Необходимо максимально ограничить вопросы, на которые может отвечать чат-бот. На данный момент ему запрещено отвечать на любые вопросы, для которых у него нет инструкции. В случае получения такого запроса он отправляет слово 'HELP', что запускает модуль GPTChatScriptAnalyzer, если тема запроса не определена, то чат будет передаваться менеджеру. Подобный подход на первый взгляд работает, однако следует провести больше тестов.



# Баги

 - Метод getRegularLessonsByLocationId класса AlfaCRMDataManager. Если урок не проведён, выдаёт ошибку. Нужно выдавать сообщение пользователю о том, что нужно провести урок. 

 -Прерывается подключение к AlfaCRM, происходит 1 раз из 10, подумать над решением.