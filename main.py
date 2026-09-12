from nicegui import ui
import psycopg
from pathlib import Path

DB = 'postgresql://postgres:Admin@localhost:5432/demoekz'
PICTURES = Path(__file__).parent / 'pictures'
PARTS = range(1, 5)
DISPLAY_ORDER = (1, 3, 2, 4)
LOCKED_MESSAGE = 'Вы заблокированы. Обратитесь к администратору'

def sql(q, p=(), many=False):
    with psycopg.connect(DB) as c:
        r = c.execute(q, p)
        return r.fetchall() if many else None

def ensure_schema():
    with psycopg.connect(DB) as c:
        c.execute(
            'ALTER TABLE users '
            'ADD COLUMN IF NOT EXISTS captcha_attempts INTEGER NOT NULL DEFAULT 0'
        )

def password_error(field, text=None):
    field.props(remove='error error-message') if text is None else field.props(
        f'error error-message="{text}"'
    )

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

                def start_drag(_, part):
                    nonlocal dragged_part
                    dragged_part = part

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
                        locked = captcha_tries >= 3
                        sql('UPDATE users SET captcha_attempts=%s,locked=%s WHERE username=%s',
                            (captcha_tries, locked, username))
                        captcha_msg.set_text(
                            LOCKED_MESSAGE if locked
                            else f'Капча собрана неверно: {captcha_tries}/3'
                        )
                        if locked:
                            msg.set_text(LOCKED_MESSAGE)
                    else:
                        captcha_msg.set_text('Неверно собранная капча засчитана только для существующего логина')
                    reset_captcha()

                for part in DISPLAY_ORDER:
                    image = ui.image(str(PICTURES / f'{part}.png')).style(image_style).props('draggable=true')
                    captcha_images[part] = image
                    image.on('dragstart', lambda event, p=part: start_drag(event, p))
                    image.move(tray)

                for expected_part in PARTS:
                    with board:
                        slot = ui.element('div').style(slot_style).props('ondragover="event.preventDefault()"')
                        captcha_slots[expected_part] = slot
                        slot.on('drop', lambda event, p=expected_part: drop_part(event, p))

                def reset_captcha():
                    nonlocal dragged_part
                    for image in captcha_images.values():
                        image.move(tray).props('draggable=true')
                    placed_parts.clear()
                    dragged_part = None
                    captcha_msg.set_text('Перетащите фрагменты на свои места')

                ui.button('Сбросить капчу', on_click=reset_captcha)

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
                rows = sql('''SELECT username,password_hash,is_admin,locked,failed_attempts
                              FROM users WHERE username=%s''',
                           ((name.value or '').strip().lower(),), True)
                if not rows:
                    password_error(pwd, 'Неверный логин или пароль')
                    msg.set_text('Неверный логин или пароль')
                    return
                user, saved, admin, locked, tries = rows[0]
                if locked: msg.set_text(LOCKED_MESSAGE); return
                if pwd.value != saved:
                    password_error(pwd, 'Неверный пароль')
                    tries += 1
                    locked = tries >= 3
                    sql('UPDATE users SET failed_attempts=%s,locked=%s WHERE username=%s',
                        (tries, locked, user))
                    msg.set_text(LOCKED_MESSAGE if locked else f'Неверный пароль: {tries}/3')
                elif admin:
                    sql('UPDATE users SET failed_attempts=0,captcha_attempts=0 WHERE username=%s', (user,))
                    admin_page()
                else:
                    sql('UPDATE users SET failed_attempts=0,captcha_attempts=0 WHERE username=%s', (user,))
                    user_page()
            ui.button('Войти', on_click=enter)

    def user_page():
        box.clear()
        with box:
            ui.label('Вы успешно авторизовались').style('text-align:center')
            ui.button('Выйти', on_click=login)

    def admin_page():
        box.clear()
        with box:
            ui.label('Пользователи').style(f'{centered};font-size:18px')
            editor = ui.column().style('width:100%;gap:8px')
            with editor:
                editor_title = ui.label('Создание пользователя').style(centered)
                edit_name, edit_password = input_field('Логин'), input_field('Пароль', True)
                form_msg = ui.label().style(centered)
                actions = ui.row().style('width:100%;justify-content:center;gap:8px')
            users = ui.column().style('width:100%;gap:8px')

            editing_id = None

            def reset_editor():
                nonlocal editing_id
                editing_id = None
                editor_title.set_text('Создание пользователя')
                edit_name.value = ''
                edit_password.value = ''
                form_msg.set_text('')

            def edit_user(uid, user):
                nonlocal editing_id
                editing_id = uid
                editor_title.set_text('Изменение пользователя')
                edit_name.value = user
                edit_password.value = ''
                form_msg.set_text('Изменение пользователя')

            def save_user():
                user = (edit_name.value or '').strip().lower()
                password = edit_password.value or ''
                if not 3 <= len(user) <= 32:
                    form_msg.set_text('Логин: от 3 до 32 символов')
                    return
                if editing_id is None and not password:
                    form_msg.set_text('Введите пароль')
                    return
                try:
                    if editing_id is None:
                        sql('''INSERT INTO users(username,password_hash,is_admin)
                               VALUES(%s,%s,FALSE)''', (user, password))
                        result = 'Пользователь добавлен'
                    else:
                        query = ('UPDATE users SET username=%s,password_hash=%s WHERE id=%s'
                                 if password else 'UPDATE users SET username=%s WHERE id=%s')
                        params = (user, password, editing_id) if password else (user, editing_id)
                        sql(query, params)
                        result = 'Пользователь изменён'
                    reset_editor()
                    form_msg.set_text(result)
                    load()
                except psycopg.errors.UniqueViolation:
                    form_msg.set_text('Такой логин уже существует')

            def load():
                users.clear()
                with users:
                    for uid, user, admin, locked in sql('SELECT id,username,is_admin,locked FROM users ORDER BY username', many=True):
                        row = ui.row().style(
                            'width:100%;display:grid;grid-template-columns:minmax(0,1fr) 96px 112px;'
                            'gap:8px;align-items:center'
                        )
                        with row:
                            ui.label(user).style('overflow:hidden;text-overflow:ellipsis;white-space:nowrap')
                            ui.button('Изменить', on_click=lambda _, i=uid, u=user: edit_user(i, u)).style('width:96px')
                            if not admin:
                                ui.button('Разблокировать' if locked else 'Удалить',
                                          on_click=lambda _, i=uid, l=locked: change(i, l)).style('width:112px')
                            else:
                                ui.element('div')
            def change(uid, locked):
                if locked:
                    sql('UPDATE users SET failed_attempts=0,captcha_attempts=0,locked=FALSE WHERE id=%s', (uid,))
                else:
                    sql('DELETE FROM users WHERE id=%s AND is_admin=FALSE', (uid,))
                load()
            with actions:
                ui.button('Сохранить', on_click=save_user).props('color=positive').style('width:112px')
                ui.button('Очистить', on_click=reset_editor).style('width:112px')
            ui.button('Выйти', on_click=login).style('width:112px')
            load()

    login()

ui.page('/')(app)

if __name__ in {'__main__', '__mp_main__'}:
    ensure_schema()
    ui.run(title='Авторизация', port=8080)