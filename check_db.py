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


def read_database_schema(connection):  # Таблицы и колонки, которые реально есть в базе
    rows = connection.execute(text("SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()")).fetchall()

    tables = {}
    for table, column in rows:
        if table not in tables:
            tables[table] = []
        tables[table].append(column)
    return tables


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

    with engine.begin() as connection:
        actual = read_database_schema(connection)

        missing_tables = []
        missing_columns = []  # (таблица, колонка, описание)

        for table in table_order:
            if table not in actual:
                missing_tables.append(table)
                continue
            for column, definition in expected[table].items():
                if column not in actual[table]:
                    missing_columns.append((table, column, definition))

        if not missing_tables and not missing_columns:
            print("✅ База в порядке: все таблицы и колонки на месте")
            return

        for table in missing_tables:
            print(f"❌ Нет таблицы: {table}")
        for table, column, definition in missing_columns:
            print(f"❌ Нет колонки: {table}.{column}  ({definition})")

        if not fix:
            print("\nЧтобы добавить недостающее, запустите: python3 check_db.py --fix")
            return

        print("\nДобавляю...")
        for table in missing_tables:
            connection.execute(text(create_statements[table]))
            print(f"✅ Создана таблица {table}")

        # Читаем базу заново: у только что созданных таблиц ещё нет колонок из ALTER TABLE
        actual = read_database_schema(connection)
        for table in table_order:
            for column, definition in expected[table].items():
                if column not in actual[table]:
                    connection.execute(text(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"))
                    print(f"✅ Добавлена колонка {table}.{column}")

        print("\nГотово! Запустите python3 check_db.py ещё раз, чтобы проверить")


if __name__ == '__main__':
    main()
