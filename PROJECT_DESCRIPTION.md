# Методичка: приложение авторизации NiceGUI + PostgreSQL

Эта методичка описывает проект полностью: от установки программ и создания базы до самостоятельного написания и запуска `main.py`. 

---

## 0. Расширения Visual Studio Code

На компьютере аудитории расширения VS Code могут отсутствовать, поэтому установите их вручную до начала работы с проектом.

Откройте VS Code и нажмите значок **Extensions** слева или сочетание клавиш `Ctrl+Shift+X`. В поле поиска по очереди найдите каждое расширение и нажмите **Install**.

### Обязательные расширения

1. **Python**
    - идентификатор: `ms-python.python`;
    - издатель: **Microsoft**;
    - нужен для запуска Python, выбора интерпретатора, запуска файлов и работы с `.venv`.

2. **Pylance**
    - идентификатор: `ms-python.vscode-pylance`;
    - издатель: **Microsoft**;
    - нужен для подсказок кода, перехода по определениям, проверки типов и обнаружения ошибок Python.

### Порядок установки

1. Откройте **Extensions** через `Ctrl+Shift+X`.
2. Найдите `Python` от издателя **Microsoft** и нажмите **Install**.
3. Найдите `Pylance` от издателя **Microsoft** и нажмите **Install**.
4. Перезапустите VS Code, если он предложит это сделать.
5. Откройте папку проекта через **File -> Open Folder**.

Отдельное расширение PostgreSQL для этого проекта не требуется: базу данных, таблицу и тестовые записи мы создаём через установленный pgAdmin 4. После установки расширения Python интерпретатор `.venv` выбирается в разделе 8.

---

## 1. Что установить

Установите:

1. Python.
2. PostgreSQL.
3. pgAdmin 4.
4. Visual Studio Code.

Во время установки PostgreSQL запомните имя пользователя, пароль и порт. В примерах ниже используются:

- пользователь: `postgres`;
- пароль: `Admin`;
- порт: `5432`.

В postgreSQL на компьютерах аудитории установленны другие данные, логин `postgres` и пароль `123`, используйте их вместо значений выше. Это данные для подключения к PostgreSQL, а не тестовые данные пользователей приложения.

Если вы указали другой пароль, его нужно будет заменить в строке подключения в `main.py`.

---

## 2. Создание базы данных

1. Откройте **pgAdmin 4**.
2. Слева раскройте `Servers` и сервер PostgreSQL.
3. Нажмите правой кнопкой на **Databases**.
4. Выберите **Create -> Database...**.
5. В поле **Database** напишите `demoekz`.
6. В поле **Owner** оставьте `postgres`.
7. Нажмите **Save**.

Если база не появилась, обновите список **Databases**.

### Альтернативный способ через SQL

Откройте Query Tool на уровне базы `postgres` и выполните:

CREATE DATABASE demoekz;

Запрос `CREATE DATABASE` нельзя выполнять внутри уже созданной базы `demoekz`.

---

## 3. Создание таблицы пользователей

1. Нажмите правой кнопкой на базу `demoekz`.
2. Выберите **Query Tool**.
3. Вставьте SQL:

CREATE TABLE IF NOT EXISTS users (
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(32) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    captcha_attempts INTEGER NOT NULL DEFAULT 0,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE
);


4. Нажмите **Execute** или клавишу `F5`.

Разбор таблицы:

- `id_user SERIAL PRIMARY KEY` автоматически создаёт уникальный номер строки;
- `username VARCHAR(32)` хранит логин длиной до 32 символов;
- `UNIQUE` запрещает два одинаковых логина;
- `NOT NULL` запрещает пустое значение;
- `password_hash` хранит пароль учебной версии;
- `is_admin` имеет тип Boolean и равен `TRUE` только у администратора;
- `failed_attempts` считает неверные попытки;
- `captcha_attempts` считает неверно собранные капчи;
- `is_locked` показывает, заблокирован ли пользователь;
- `DEFAULT FALSE` задаёт значение `FALSE`, если его не передали.

---

## 4. Заполнение тестовыми данными

В том же Query Tool создайте администратора:

INSERT INTO users (
    username,
    password_hash,
    is_admin,
    failed_attempts,
    captcha_attempts,
    is_locked
)
VALUES (
    'admin',
    'AdminPassword',
    TRUE,
    0,
    0,
    FALSE
)
ON CONFLICT (username) DO NOTHING;

Данные администратора:

- логин: `admin`;
- пароль: `AdminPassword`.

`ON CONFLICT (username) DO NOTHING` означает: если такой логин уже есть, не создавать вторую строку и не выдавать ошибку.

Добавьте обычного пользователя для проверки блокировки:

INSERT INTO users (
    username,
    password_hash,
    is_admin,
    failed_attempts,
    captcha_attempts,
    is_locked
)
VALUES (
    'user1',
    'UserPassword1',
    FALSE,
    0,
    0,
    FALSE
)
ON CONFLICT (username) DO NOTHING;

Проверить данные можно так:

SELECT * FROM users;

---

## 5. Создание проекта и картинок

Создайте папку, например:

C:\Users\ВашеИмя\NiceGuiDBekz

Откройте её в VS Code через **File -> Open Folder**.

Итоговая структура до написания программы:

NiceGuiDBekz/
├── main.py
└── pictures/
    ├── 1.png
    ├── 2.png
    ├── 3.png
    └── 4.png

Создайте файл `main.py` и папку `pictures`. Положите картинки в `pictures` рядом с `main.py`.

Имена должны быть точными: `1.png`, `2.png`, `3.png`, `4.png`.

Соответствие фрагментов:

- `1.png` — левый верхний фрагмент;
- `2.png` — правый верхний;
- `3.png` — левый нижний;
- `4.png` — правый нижний.

Картинки нельзя помещать внутрь `.venv`.

---

## 6. Создание виртуального окружения

Откройте **Terminal -> New Terminal** в VS Code.

Перейдите в папку проекта:

cd C:\Users\ВашеИмя\NiceGuiDBekz

Создайте окружение:

python -m venv .venv

Здесь `python -m venv` запускает встроенный модуль Python для создания изолированного окружения, а `.venv` — имя папки окружения.

Активируйте его:

.\.venv\Scripts\Activate.ps1

После успешной активации в начале строки терминала появится `(.venv)`.

Если PowerShell запрещает запуск скриптов, один раз выполните:

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Подтвердите `Y`, затем снова выполните:

.\.venv\Scripts\Activate.ps1

---

## 7. Установка двух библиотек

Отдельный файл `requirements.txt` для этого проекта не нужен. Библиотек всего две, поэтому установите их отдельными командами в активированное `.venv`.

Первая библиотека создаёт веб-интерфейс:

python -m pip install nicegui

Вторая библиотека соединяет Python с PostgreSQL:

python -m pip install "psycopg[binary]"

`python -m pip` означает: запустить `pip` именно через тот Python, который сейчас выбран. Поэтому пакеты попадут в активированное `.venv`.

Проверка установки:

python -c "from nicegui import ui; import psycopg; print('Библиотеки установлены')"

В команде `-c` Python получает короткий код как текст, импортирует обе библиотеки и печатает сообщение.

---

## 8. Выбор Python в VS Code

1. Нажмите `Ctrl+Shift+P`.
2. Выполните команду **Python: Select Interpreter**.
3. Выберите `.venv\Scripts\python.exe`.

VS Code должен использовать тот же Python, куда установлены NiceGUI и psycopg.

Проверка:

python --version
python -m pip show nicegui
python -m pip show psycopg

---

## 9. Архитектура проекта

В проекте один файл с программой и одна папка с картинками:

NiceGuiDBekz/
├── main.py       # весь Python-код
└── pictures/     # 1.png, 2.png, 3.png, 4.png

Логика `main.py` идёт сверху вниз:

1. импорты библиотек;
2. строка подключения и пути;
3. порядок показа картинок и сообщение блокировки;
4. общая функция SQL;
5. функция обновления схемы базы;
6. функция показа ошибки пароля;
7. функция `app`, создающая общий контейнер;
8. `login`, форма входа и капча;
9. `enter`, проверяющая логин;
10. `user_page`, страница обычного пользователя;
11. `admin_page`, панель администратора;
12. регистрация страницы и запуск сервера.

`login`, `user_page` и `admin_page` являются вложенными функциями `app`, потому что им нужен общий контейнер `box`.

---

## 10. Написание `main.py` с нуля

Откройте пустой `main.py`. Все блоки ниже добавляйте сверху вниз. 

### 10.1. Импорты

Первая строка:

from nicegui import ui

`from ... import ...` берёт объект `ui` из библиотеки `nicegui`. Через `ui` создаются подписи, поля, кнопки, изображения и страница.

Вторая строка:

import psycopg

`import` подключает библиотеку целиком. `psycopg` нужен для соединения с PostgreSQL.

Третья строка:

from pathlib import Path

`Path` — стандартный класс Python для работы с путями файлов и папок. Его не нужно устанавливать отдельно.

В начале файла должно быть:

from nicegui import ui
import psycopg
from pathlib import Path

### 10.2. Настройки

DB = 'postgresql://postgres:Admin@localhost:5432/demoekz'

`DB` — имя переменной. В строке подключения находятся схема, пользователь, пароль, адрес, порт и база:

- `postgresql` — используем PostgreSQL;
- `postgres` — пользователь;
- `Admin` — пароль;
- `localhost` — этот компьютер;
- `5432` — порт;
- `demoekz` — база.

В примере пароль PostgreSQL — `Admin`. В PostgreSQL на пк в аудиториях, пароль будет `123`, строка будет такой:

```python
DB = 'postgresql://postgres:123@localhost:5432/demoekz'
```

Тестовые данные приложения при этом не меняются: логин администратора `admin`, пароль `AdminPassword`; обычный пользователь — `user1`, пароль `UserPassword1`.

PICTURES = Path(__file__).parent / 'pictures'

`__file__` означает путь к текущему файлу `main.py`. `.parent` получает папку, где находится файл. Оператор `/` у `Path` добавляет к ней папку `pictures`.

PARTS = range(1, 5)

`range(1, 5)` создаёт последовательность `1`, `2`, `3`, `4`. Число `5` не включается.

DISPLAY_ORDER = (1, 3, 2, 4)

`DISPLAY_ORDER` задаёт порядок картинок в верхнем лотке. Поэтому на экране они появляются не по порядку.

LOCKED_MESSAGE = 'Вы заблокированы. Обратитесь к администратору'

Эта константа хранит единый текст, который показывается при блокировке по паролю или по капче.

### 10.3. Общая функция SQL

def sql(q, p=(), many=False):
    with psycopg.connect(DB) as c:
        r = c.execute(q, p)
        return r.fetchall() if many else None

Разбор построчно:

def sql(q, p=(), many=False):

`def` объявляет функцию. Имя функции — `sql`. Она принимает:

- `q` — текст SQL-запроса;
- `p=()` — параметры запроса, по умолчанию пустой кортеж;
- `many=False` — флаг, нужно ли вернуть строки результата.

    with psycopg.connect(DB) as c:

`psycopg.connect(DB)` открывает соединение с базой. `with` создаёт контекст: после блока соединение будет закрыто автоматически. `as c` сохраняет соединение в переменную `c`. Четыре пробела показывают, что строка находится внутри функции.

        r = c.execute(q, p)

`execute` отправляет запрос в PostgreSQL. `q` — сам запрос, `p` — значения для мест `%s` внутри запроса. Результат сохраняется в `r`.

        return r.fetchall() if many else None

`return` возвращает результат из функции. Это условное выражение: если `many` равен `True`, вызывается `fetchall()` и возвращаются все строки; иначе возвращается `None`.

Пример безопасного чтения:

rows = sql(
    'SELECT username FROM users WHERE username=%s',
    ('admin',),
    True,
)

Значение передаётся отдельно от SQL. Не вставляйте логин в запрос сложением строк.

### 10.4. Обновление схемы базы

def ensure_schema():
    with psycopg.connect(DB) as c:
        c.execute(
            'ALTER TABLE users '
            'ADD COLUMN IF NOT EXISTS captcha_attempts INTEGER NOT NULL DEFAULT 0'
        )
`ensure_schema` нужна для уже существующих баз, созданных до добавления счётчика капч. `ADD COLUMN IF NOT EXISTS` добавляет столбец только при его отсутствии, поэтому повторный запуск безопасен. Если столбец уже есть, PostgreSQL ничего не меняет.

### 10.5. Функция ошибки пароля

def password_error(field, text=None):
    field.props(remove='error error-message') if text is None else field.props(
        f'error error-message="{text}"'
    )

def password_error(field, text=None):

Функция получает объект поля `field` и необязательный текст `text`. Если текст не передали, он равен `None`.

    field.props(remove='error error-message') if text is None else field.props(

`props` изменяет свойства элемента NiceGUI. Если текста нет, удаляются свойства ошибки. Конструкция `A if условие else B` выбирает одну из двух операций.

        f'error error-message="{text}"'

`f` перед строкой позволяет вставить значение переменной `{text}` внутрь строки. Здесь формируется свойство с сообщением ошибки.

### 10.6. Функция приложения и общий контейнер

def app():
    centered = 'width:100%;text-align:center'
    input_field = lambda label, password=False: ui.input(label, password=password).style('width:100%')
    with ui.element('div').style(
        'width:100%;min-height:100vh;box-sizing:border-box;padding:24px;'
        'display:flex;align-items:center;justify-content:center'
    ):
        box = ui.column().style(
            'width:360px;max-width:100%;align-items:center;gap:12px'
        )

def app():

Создаёт функцию, которая строит интерфейс.

    centered = 'width:100%;text-align:center'

Сохраняет CSS-стиль выравнивания текста по центру.

    input_field = lambda label, password=False: ui.input(label, password=password).style('width:100%')

`lambda` создаёт короткую функцию без отдельного имени `def`. Она получает подпись `label` и флаг `password`, создаёт поле NiceGUI и задаёт ему ширину 100 процентов.

    with ui.element('div').style(

Создаёт HTML-элемент `div` и открывает контекст его содержимого.

        'width:100%;min-height:100vh;box-sizing:border-box;padding:24px;'
        'display:flex;align-items:center;justify-content:center'

Это CSS. Две соседние строковые константы Python автоматически объединяет в одну строку. Контейнер занимает ширину окна, имеет минимальную высоту окна, внутренний отступ и центрирует содержимое через Flexbox.

    ):

Закрывает вызов `.style(...)`. Двоеточие начинает тело `with`.

        box = ui.column().style(
            'width:360px;max-width:100%;align-items:center;gap:12px'
        )

`ui.column()` создаёт вертикальный контейнер. `box` будет содержать текущий экран. `.style(...)` задаёт ширину, ограничение по ширине, выравнивание и расстояние между элементами.

### 10.7. Экран входа

Эта функция должна находиться внутри `app`, поэтому перед `def` четыре пробела:

    def login(note=''):
        box.clear()
        with box:
            ui.label('Авторизация').style(centered)
            name, pwd = input_field('Логин'), input_field('Пароль', True)
            msg = ui.label(note).style(centered)

            dragged_part = None
            placed_parts = {}
            captcha_msg = ui.label('Перетащите фрагменты на свои места').style(centered)
            captcha_area = ui.column().style('width:100%;gap:12px;align-items:center')
            image_style = (
                'width:78px;height:78px;box-sizing:border-box;object-fit:cover;'
                'cursor:grab;border:2px solid #9e9e9e'
            )
            slot_style = (
                'width:78px;height:78px;box-sizing:border-box;border:2px dashed #9e9e9e;'
                'display:flex;flex-direction:column;align-items:center;justify-content:center;'
                'overflow:hidden;padding:0;background:#f5f5f5'
            )

    def login(note=''):

Создаёт функцию экрана входа. `note=''` позволяет передать необязательное сообщение.

        box.clear()

`clear()` удаляет дочерние элементы контейнера `box`. Так старый экран исчезает перед созданием нового.

        with box:

Все следующие элементы добавляются внутрь `box`.

            ui.label('Авторизация').style(centered)

Создаёт текстовую подпись и применяет ранее сохранённый стиль.

            name, pwd = input_field('Логин'), input_field('Пароль', True)

Создаёт два поля. `name` хранит поле логина, `pwd` — поле пароля. `True` включает скрытие пароля.

            msg = ui.label(note).style(centered)

Создаёт пустую или переданную подпись. Позже её текст меняется через `msg.set_text(...)`. Метод `set_text` заменяет текст существующего элемента, не создавая новый элемент.

            dragged_part = None
            placed_parts = {}

Сначала нет перетаскиваемой части. Словарь `placed_parts` будет хранить пары: номер слота и номер поставленной в него части.

Следующие строки создают сообщение капчи, контейнер и CSS-стили картинок и слотов. Скобки позволяют разбить длинную строку на несколько физических строк.

### 10.8. Лоток и обработчики капчи

            with captcha_area:
                tray = ui.row().style(
                    'width:100%;min-height:90px;gap:8px;flex-wrap:wrap;'
                    'justify-content:center'
                )
                board = ui.element('div').style(
                    'width:100%;display:grid;grid-template-columns:78px 78px;gap:8px;justify-content:center'
                )
                captcha_images = {}
                captcha_slots = {}

`captcha_area` становится родителем. `ui.row()` создаёт горизонтальный лоток. `board` создаёт HTML-сетку с двумя колонками. Пустые словари будут связывать номера частей и слотов с объектами NiceGUI.

                def start_drag(_, part):
                    nonlocal dragged_part
                    dragged_part = part

Обработчик получает событие в `_`, но событие не используется. `nonlocal` разрешает изменять переменную `dragged_part` из внешней функции `login`.

                def drop_part(_, expected_part):
                    nonlocal dragged_part
                    if dragged_part is None:
                        return
                    if expected_part in placed_parts:
                        captcha_msg.set_text('Это место уже занято')
                        dragged_part = None
                        return
                    captcha_images[dragged_part].move(captcha_slots[expected_part]).props('draggable=false')
                    placed_parts[expected_part] = dragged_part
                    dragged_part = None
                    if len(placed_parts) != len(PARTS):
                        captcha_msg.set_text(f'Размещено: {len(placed_parts)}/{len(PARTS)}')
                        return
                    if all(placed_parts.get(part) == part for part in PARTS):
                        captcha_msg.set_text('Капча пройдена')
                        return
                    username = (name.value or '').strip().lower()
                    rows = sql('SELECT captcha_attempts FROM users WHERE username=%s', (username,), True)
                    if rows:
                        captcha_tries = rows[0][0] + 1
                        is_locked = captcha_tries >= 3
                        sql('UPDATE users SET captcha_attempts=%s,is_locked=%s WHERE username=%s',
                            (captcha_tries, is_locked, username))
                        captcha_msg.set_text(
                            LOCKED_MESSAGE if is_locked
                            else f'Капча собрана неверно: {captcha_tries}/3'
                        )
                        if is_locked:
                            msg.set_text(LOCKED_MESSAGE)
                    else:
                        captcha_msg.set_text('Неверно собранная капча засчитана только для существующего логина')
                    reset_captcha()

`drop_part` вызывается при отпускании картинки. Если слот уже есть в `placed_parts`, новая картинка туда не ставится. Словарь хранит номер слота и номер детали, поэтому одна деталь не может занять уже заполненное место. После заполнения четырёх слотов программа сравнивает каждую пару. Неверная полная сборка увеличивает `captcha_attempts`, а после третьей такой сборки устанавливает `is_locked`.

### 10.9. Создание изображений, слотов и сброс

                for part in DISPLAY_ORDER:
                    image = ui.image(str(PICTURES / f'{part}.png')).style(image_style).props('draggable=true')
                    captcha_images[part] = image
                    image.on('dragstart', lambda event, p=part: start_drag(event, p))
                    image.move(tray)

`for` повторяет тело для номеров 1–4. `f'{part}.png'` создаёт имя файла. `str` превращает `Path` в строку. `.on` подключает обработчик события. `p=part` сохраняет номер текущей итерации для конкретной картинки. `.move(tray)` помещает изображение в лоток.

                for expected_part in PARTS:
                    with board:
                        slot = ui.element('div').style(slot_style).props('ondragover="event.preventDefault()"')
                        captcha_slots[expected_part] = slot
                        slot.on('drop', lambda event, p=expected_part: drop_part(event, p))

Второй цикл создаёт четыре слота. `with board` делает слот дочерним элементом сетки. `event.preventDefault()` разрешает браузеру принять перетаскиваемый элемент. `slot.on('drop', ...)` запускает проверку при отпускании.

                def reset_captcha():
                    nonlocal dragged_part
                    for image in captcha_images.values():
                        image.move(tray).props('draggable=true')
                    placed_parts.clear()
                    dragged_part = None
                    captcha_msg.set_text('Перетащите фрагменты на свои места')

                ui.button('Сбросить капчу', on_click=reset_captcha)

`values()` перебирает объекты словаря. `clear()` у словаря удаляет все пары занятых слотов. Функция возвращает картинки, снова включает перетаскивание и возвращает исходное сообщение. Кнопка запускает её через `on_click`.

### 10.10. Проверка входа

            def enter():
                if len(placed_parts) != len(PARTS) or not all(
                    placed_parts.get(part) == part for part in PARTS
                ):
                    msg.set_text('Сначала правильно соберите пазл')
                    return
                password_error(pwd)
                if not (pwd.value or '').strip():
                    password_error(pwd, 'Введите пароль')
                    msg.set_text('Введите пароль')
                    return
                rows = sql('''SELECT username,password_hash,is_admin,is_locked,failed_attempts
                              FROM users WHERE username=%s''',
                           ((name.value or '').strip().lower(),), True)
                if not rows:
                    password_error(pwd, 'Неверный логин или пароль')
                    msg.set_text('Неверный логин или пароль')
                    return
                user, saved, admin, is_locked, tries = rows[0]
                if is_locked: msg.set_text(LOCKED_MESSAGE); return
                if pwd.value != saved:
                    password_error(pwd, 'Неверный пароль')
                    tries += 1
                    is_locked = tries >= 3
                    sql('UPDATE users SET failed_attempts=%s,is_locked=%s WHERE username=%s',
                        (tries, is_locked, user))
                    msg.set_text(LOCKED_MESSAGE if is_locked else f'Неверный пароль: {tries}/3')
                elif admin:
                    sql('UPDATE users SET failed_attempts=0,captcha_attempts=0 WHERE username=%s', (user,))
                    admin_page()
                else:
                    sql('UPDATE users SET failed_attempts=0,captcha_attempts=0 WHERE username=%s', (user,))
                    user_page()
            ui.button('Войти', on_click=enter)

Порядок работы:

1. Проверяется, что в `placed_parts` заняты все четыре слота и каждая деталь стоит на своём месте.
2. Старое сообщение ошибки очищается вызовом уже описанной `password_error`.
3. `pwd.value` получает значение поля. `or ''` заменяет `None` пустой строкой, `strip()` убирает пробелы.
4. SQL выбирает пользователя по логину. `lower()` приводит логин к нижнему регистру.
5. Если `rows` пуст, пользователь не найден.
6. `rows[0]` берёт первую строку результата, а присваивание раскладывает пять значений по переменным.
7. Если `is_locked` истинен, показывается сообщение `Вы заблокированы. Обратитесь к администратору`.
8. Неверный пароль увеличивает `tries`. `tries >= 3` даёт Boolean для поля `is_locked`.
9. При правильном пароле оба счётчика ошибок сбрасываются в `0`.
10. Затем администратор получает `admin_page()`, обычный пользователь — `user_page()`.
11. `ui.button(..., on_click=enter)` создаёт кнопку и связывает её с функцией.

### 10.11. Страница обычного пользователя

    def user_page():
        box.clear()
        with box:
            ui.label('Вы успешно авторизовались').style('text-align:center')
            ui.button('Выйти', on_click=login)

Функция очищает контейнер, создаёт сообщение и кнопку. При нажатии кнопка вызывает уже созданную `login`.

### 10.12. Панель администратора: форма

    def admin_page():
        box.clear()
        with box:
            ui.label('Пользователи').style(centered)
            editor = ui.column().style('width:100%;gap:8px')
            with editor:
                editor_title = ui.label('Создание пользователя').style(centered)
                edit_name, edit_password = input_field('Логин'), input_field('Пароль', True)
                form_msg = ui.label().style(centered)
                actions = ui.row().style('width:100%;justify-content:center;gap:8px')
            users = ui.column().style('width:100%;gap:8px')

            editing_id_user = None

Создаются заголовок, подпись режима, поля редактирования, сообщение, ряд кнопок и контейнер списка. `editor_title` сначала показывает `Создание пользователя`, а `editing_id_user = None` означает создание нового пользователя.

            def reset_editor():
                nonlocal editing_id_user
                editing_id_user = None
                editor_title.set_text('Создание пользователя')
                edit_name.value = ''
                edit_password.value = ''
                form_msg.set_text('')

            def edit_user(id_user, user):
                nonlocal editing_id_user
                editing_id_user = id_user
                editor_title.set_text('Изменение пользователя')
                edit_name.value = user
                edit_password.value = ''
                form_msg.set_text('Изменение пользователя')

`reset_editor` возвращает подпись в режим `Создание пользователя`, очищает значения полей и сообщение. `edit_user` меняет подпись на `Изменение пользователя`, запоминает идентификатор и логин выбранной записи. Свойство `.value` читает или изменяет значение поля.
### 10.13. Панель администратора: сохранение

            def save_user():
                user = (edit_name.value or '').strip().lower()
                password = edit_password.value or ''
                if not 3 <= len(user) <= 32:
                    form_msg.set_text('Логин: от 3 до 32 символов')
                    return
                if editing_id_user is None and not password:
                    form_msg.set_text('Введите пароль')
                    return
                try:
                    if editing_id_user is None:
                        sql('''INSERT INTO users(username,password_hash,is_admin)
                               VALUES(%s,%s,FALSE)''', (user, password))
                        result = 'Пользователь добавлен'
                    else:
                        query = ('UPDATE users SET username=%s,password_hash=%s WHERE id_user=%s'
                                 if password else 'UPDATE users SET username=%s WHERE id_user=%s')
                        params = (user, password, editing_id_user) if password else (user, editing_id_user)
                        sql(query, params)
                        result = 'Пользователь изменён'
                    reset_editor()
                    form_msg.set_text(result)
                    load()
                except psycopg.errors.UniqueViolation:
                    form_msg.set_text('Такой логин уже существует')

`if not 3 <= len(user) <= 32` проверяет длину логина. `try` начинает блок, в котором возможна ошибка базы. В режиме создания выполняется `INSERT`, в режиме изменения `UPDATE`. Если пароль пуст, старый пароль сохраняется. `except` ловит ошибку уникального логина. `load()` обновляет список.

### 10.14. Панель администратора: список

            def load():
                users.clear()
                with users:
                    for id_user, user, admin, is_locked in sql('SELECT id_user,username,is_admin,is_locked FROM users ORDER BY username', many=True):
                        row = ui.row().style(
                            'width:100%;display:grid;grid-template-columns:minmax(0,1fr) 96px 112px;'
                            'gap:8px;align-items:center'
                        )
                        with row:
                            ui.label(user).style('overflow:hidden;text-overflow:ellipsis;white-space:nowrap')
                            ui.button('Изменить', on_click=lambda _, i=id_user, u=user: edit_user(i, u)).style('width:96px')
                            if not admin:
                                ui.button('Разблокировать' if is_locked else 'Удалить',
                                          on_click=lambda _, i=id_user, l=is_locked: change(i, l)).style('width:112px')
                            else:
                                ui.element('div')

`users.clear()` очищает старый список. SQL возвращает четыре значения каждой строки. `row` — строка интерфейса. У администратора вместо кнопки удаления создаётся пустой `div`. `lambda` сохраняет обработчик для конкретного пользователя; параметры `i=id_user`, `u=user` и `l=is_locked` фиксируют текущие значения цикла.

Добавьте изменение и кнопки:

            def change(id_user, is_locked):
                if is_locked:
                    sql('UPDATE users SET failed_attempts=0,is_locked=FALSE WHERE id_user=%s', (id_user,))
                else:
                    sql('DELETE FROM users WHERE id_user=%s AND is_admin=FALSE', (id_user,))
                load()
            with actions:
                ui.button('Сохранить', on_click=save_user).props('color=positive').style('width:112px')
                ui.button('Очистить', on_click=reset_editor).style('width:112px')
            ui.button('Выйти', on_click=login).style('width:112px')
            load()

Если пользователь заблокирован, `change` сбрасывает оба счётчика и `is_locked`. Иначе удаляется только строка с `is_admin=FALSE`. Затем список загружается заново. Кнопки запускают сохранение, очистку и выход.

### 10.15. Завершение файла

После всех функций, но внутри `app`, добавьте:

    login()

Этот вызов показывает первый экран при открытии приложения.

Без отступа, после завершения `app`, добавьте:

ui.page('/')(app)

Корневой адрес `/` связывается с функцией `app`.

Последний блок:

if __name__ in {'__main__', '__mp_main__'}:
    ensure_schema()
    ui.run(title='Авторизация', port=8080)

`__name__` показывает способ запуска файла. Условие разрешает запуск сервера при прямом запуске `python main.py`. `ensure_schema()` добавляет недостающий столбец счётчика капч в старую базу. `ui.run` запускает NiceGUI с заголовком и портом `8080`.

### 10.16. Проверка отступов

Внутри `app` должны находиться с отступом:

- `login`;
- `user_page`;
- `admin_page`.

Внутри `login` должны находиться обработчики капчи и `enter`. Внутри `admin_page` должны находиться функции формы и списка. Строки `ui.page('/')`, `if __name__...` и `ui.run` должны начинаться без пробелов.

Проверить синтаксис можно командой:

python -m py_compile main.py

---

## 11. Первый запуск

Убедитесь, что PostgreSQL запущен, база `demoekz` и таблица `users` созданы, тестовые данные добавлены, картинки лежат в `pictures`, а `.venv` активирован.

cd C:\Users\ВашеИмя\NiceGuiDBekz
.\.venv\Scripts\Activate.ps1
python main.py

Откройте в браузере:

http://localhost:8080

Ожидаемое сообщение:

NiceGUI ready to go on http://localhost:8080

Остановить сервер можно через `Ctrl+C`.

---

## 12. Проверка проекта

1. Соберите капчу.
2. Войдите как `admin` с паролем `AdminPassword`.
3. Добавьте обычного пользователя в панели.
4. Три раза введите неверный пароль.
5. Убедитесь, что появилось сообщение `Вы заблокированы. Обратитесь к администратору`.
6. Нажмите **Разблокировать**.
7. Соберите капчу неправильно три раза: каждый фрагмент можно ставить в любое свободное место, но занятое место повторно выбрать нельзя.
8. Убедитесь, что пользователь снова заблокирован тем же сообщением.
9. Нажмите **Разблокировать** и войдите с правильным паролем.
10. Убедитесь, что после успешной авторизации счётчики неправильных паролей и капч сбросились.
11. Проверьте изменение, удаление и кнопку сброса капчи.

---

## 13. Частые ошибки

### `No module named 'nicegui'`

Активируйте `.venv` и выполните:

python -m pip install nicegui

### `No module named 'psycopg'`

Активируйте `.venv` и выполните:

python -m pip install "psycopg[binary]"

### Ошибка подключения к базе

Проверьте, что PostgreSQL запущен, база называется `demoekz`, пользователь и пароль в `DB` правильные, а таблица создана именно в базе `demoekz`.

### Картинки не отображаются

Проверьте, что рядом с `main.py` находится папка `pictures`, а имена файлов точно равны `1.png`, `2.png`, `3.png`, `4.png`.

### Порт `8080` занят

Остановите старое приложение через `Ctrl+C` или временно измените `port=8080` на другой свободный порт.

