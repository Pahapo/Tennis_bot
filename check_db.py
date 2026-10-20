# Проверка базы данных: сравнивает таблицы и колонки в вашей базе с tennisDB_script.sql
#
#   python3 check_db.py         — показать, чего не хватает
#   python3 check_db.py --fix   — добавить недостающие таблицы и колонки (данные не трогает)
#
# Адрес базы берётся из DATABASE_URL в .env

import os
import re
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

SCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tennisDB_script.sql')


def read_expected_schema():  # Таблицы и колонки из tennisDB_script.sql
    with open(SCRIPT_FILE, encoding='utf-8') as file:
        sql = file.read()

    tables = {}            # {таблица: {колонка: описание}}
    create_statements = {} # {таблица: CREATE TABLE ...}
    table_order = []       # В каком порядке создавать (из-за внешних ключей)

    # CREATE TABLE `имя` ( ... );
    for match in re.finditer(r"CREATE TABLE `(\w+)` \((.*?)\n\);", sql, re.S):
        table = match.group(1)
        tables[table] = {}
        create_statements[table] = match.group(0)
        table_order.append(table)

        for line in match.group(2).split('\n'):
            line = line.strip().rstrip(',')
            column = re.match(r"`(\w+)` (.+)", line)
            if column:
                tables[table][column.group(1)] = column.group(2)

    # ALTER TABLE `имя` ADD COLUMN `колонка` описание
    for match in re.finditer(r"ALTER TABLE `(\w+)`(.*?);", sql, re.S):
        table = match.group(1)
        for column in re.finditer(r"ADD COLUMN `(\w+)` ([^,;]+)", match.group(2)):
            tables[table][column.group(1)] = column.group(2).strip()

    return tables, create_statements, table_order


def read_database_schema(connection):  # Таблицы и колонки, которые реально есть в базе: {таблица: {колонка: (тип, extra)}}
    rows = connection.execute(text("SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()")).fetchall()

    tables = {}
    for table, column, column_type, extra in rows:
        if table not in tables:
            tables[table] = {}
        tables[table][column] = (column_type.lower(), extra.lower())
    return tables


INTEGER_TYPES = ('int', 'bigint', 'smallint', 'tinyint', 'mediumint')


def plan_column_changes(expected, actual, table_order):  # Что поменять в уже существующих таблицах: [(сообщение, SQL)]
    changes = []

    for table in table_order:
        if table not in actual:
            continue

        for column, definition in expected[table].items():
            if column not in actual[table]:

                # Колонка-счётчик (AUTO_INCREMENT) может быть только одна. Если в старой таблице она называлась
                # по-другому (например, payment.id_player), переименовываем её, а не добавляем вторую
                if 'auto_increment' in definition.lower():
                    old_column = None
                    for name, info in actual[table].items():
                        if 'auto_increment' in info[1] and name not in expected[table]:
                            old_column = name

                    if old_column:
                        changes.append((f"Переименовать колонку {table}.{old_column} → {column}", f"ALTER TABLE `{table}` CHANGE COLUMN `{old_column}` `{column}` {definition}"))
                    else:
                        changes.append((f"Добавить колонку {table}.{column}  ({definition})", f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition} PRIMARY KEY"))
                    continue

                changes.append((f"Добавить колонку {table}.{column}  ({definition})", f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"))
                continue

            # Число -> строка (например, payment.price int -> varchar(10)) — безопасно, данные не теряются
            expected_type = definition.split()[0].lower()
            actual_type = actual[table][column][0]
            if expected_type.startswith('varchar') and actual_type.startswith(INTEGER_TYPES):
                changes.append((f"Сменить тип {table}.{column}: {actual_type} → {expected_type}", f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` {definition}"))

    return changes


def run(connection, message, sql):  # Выполнить одно изменение; ошибка не останавливает остальные
    try:
        connection.execute(text(sql))
        print(f"✅ {message}")
    except Exception as e:
        print(f"❌ Не получилось: {message}\n   {e.__class__.__name__}: {e.orig if hasattr(e, 'orig') else e}")


def main():
    fix = '--fix' in sys.argv

    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ В .env нет DATABASE_URL")
        return

    # Скрипт работает без asyncio, поэтому подключаемся обычным драйвером pymysql
    database_url = database_url.replace('mysql+aiomysql://', 'mysql+pymysql://')
    engine = create_engine(database_url)

    expected, create_statements, table_order = read_expected_schema()

    # В MySQL изменения структуры (CREATE / ALTER) сохраняются сразу, поэтому отдельные транзакции не нужны
    with engine.connect() as connection:
        actual = read_database_schema(connection)

        missing_tables = []
        for table in table_order:
            if table not in actual:
                missing_tables.append(table)

        changes = plan_column_changes(expected, actual, table_order)

        if not missing_tables and not changes:
            print("✅ База в порядке: все таблицы и колонки на месте")
            return

        for table in missing_tables:
            print(f"❌ Нет таблицы: {table}")
        for message, sql in changes:
            print(f"❌ {message}")

        if not fix:
            print("\nЧтобы исправить, запустите: python3 check_db.py --fix")
            return

        print("\nИсправляю...")
        for table in missing_tables:
            run(connection, f"Создать таблицу {table}", create_statements[table])

        # Читаем базу заново: у только что созданных таблиц ещё нет колонок из ALTER TABLE
        actual = read_database_schema(connection)
        for message, sql in plan_column_changes(expected, actual, table_order):
            run(connection, message, sql)

        connection.commit()
        print("\nГотово! Запустите python3 check_db.py ещё раз, чтобы проверить")


if __name__ == '__main__':
    main()
