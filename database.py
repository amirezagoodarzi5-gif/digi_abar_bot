import sqlite3

DB = "bot.db"


def connect():
    return sqlite3.connect(DB)


def init_db():
    db = connect()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER,
        user_id INTEGER,
        warnings INTEGER DEFAULT 0,
        title TEXT DEFAULT '',
        role TEXT DEFAULT 'member',
        PRIMARY KEY(chat_id, user_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        chat_id INTEGER,
        name TEXT,
        value TEXT,
        PRIMARY KEY(chat_id, name)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rules (
        chat_id INTEGER PRIMARY KEY,
        text TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        chat_id INTEGER,
        user_id INTEGER,
        messages INTEGER DEFAULT 0,
        PRIMARY KEY(chat_id, user_id)
    )
    """)

    db.commit()
    db.close()


def execute(query, params=()):
    db = connect()
    cur = db.cursor()
    cur.execute(query, params)
    db.commit()
    result = cur.fetchall()
    db.close()
    return result


def add_warning(chat_id, user_id):
    execute("""
    INSERT INTO users(chat_id, user_id, warnings)
    VALUES (?, ?, 1)
    ON CONFLICT(chat_id, user_id)
    DO UPDATE SET warnings = warnings + 1
    """, (chat_id, user_id))


def get_warnings(chat_id, user_id):
    result = execute("""
    SELECT warnings FROM users
    WHERE chat_id=? AND user_id=?
    """, (chat_id, user_id))

    return result[0][0] if result else 0


def set_title(chat_id, user_id, title):
    execute("""
    INSERT INTO users(chat_id, user_id, title)
    VALUES (?, ?, ?)
    ON CONFLICT(chat_id, user_id)
    DO UPDATE SET title=excluded.title
    """, (chat_id, user_id, title))


def get_title(chat_id, user_id):
    result = execute("""
    SELECT title FROM users
    WHERE chat_id=? AND user_id=?
    """, (chat_id, user_id))

    return result[0][0] if result else ""


def set_role(chat_id, user_id, role):
    execute("""
    INSERT INTO users(chat_id, user_id, role)
    VALUES (?, ?, ?)
    ON CONFLICT(chat_id, user_id)
    DO UPDATE SET role=excluded.role
    """, (chat_id, user_id, role))


def get_role(chat_id, user_id):
    result = execute("""
    SELECT role FROM users
    WHERE chat_id=? AND user_id=?
    """, (chat_id, user_id))

    return result[0][0] if result else "member"


def set_setting(chat_id, name, value):
    execute("""
    INSERT INTO settings(chat_id, name, value)
    VALUES (?, ?, ?)
    ON CONFLICT(chat_id, name)
    DO UPDATE SET value=excluded.value
    """, (chat_id, name, value))


def get_setting(chat_id, name):
    result = execute("""
    SELECT value FROM settings
    WHERE chat_id=? AND name=?
    """, (chat_id, name))

    return result[0][0] if result else "off"


def set_rules(chat_id, text):
    execute("""
    INSERT INTO rules(chat_id, text)
    VALUES (?, ?)
    ON CONFLICT(chat_id)
    DO UPDATE SET text=excluded.text
    """, (chat_id, text))


def get_rules(chat_id):
    result = execute(
        "SELECT text FROM rules WHERE chat_id=?",
        (chat_id,)
    )

    return result[0][0] if result else "قوانین تنظیم نشده است."


def add_message(chat_id, user_id):
    execute("""
    INSERT INTO stats(chat_id, user_id, messages)
    VALUES (?, ?, 1)
    ON CONFLICT(chat_id, user_id)
    DO UPDATE SET messages = messages + 1
    """, (chat_id, user_id))


def get_stats(chat_id):
    result = execute("""
    SELECT COUNT(*), COALESCE(SUM(messages), 0)
    FROM stats WHERE chat_id=?
    """, (chat_id,))

    return result[0]
