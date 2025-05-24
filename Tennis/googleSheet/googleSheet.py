import time
import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from aiogram.enums import ParseMode
from config.config import EMAILS

from config.db import session
from models.Division import Division


# --- Авторизация через Google Sheets и Drive API -----
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive']

creds_sheets = Credentials.from_service_account_file('credentials_tennisbot.json', scopes=SCOPES_SHEETS)
creds_drive = Credentials.from_service_account_file('credentials_tennisbot.json', scopes=SCOPES_DRIVE)

service_sheets = build('sheets', 'v4', credentials=creds_sheets)
service_drive = build('drive', 'v3', credentials=creds_drive)



def createNewSheet(source_spreadsheet_id, nameTournament):
    # --- Создание копии таблицы -----
    copied_file = service_drive.files().copy(
        fileId=source_spreadsheet_id,
        body={'name': nameTournament}
    ).execute()
    new_spreadsheet_id = copied_file['id']

    print(f"Таблица скопирована: {copied_file['name']}, LINK: https://docs.google.com/spreadsheets/d/{new_spreadsheet_id}")
    # !!! --- ЗАПРОС В БД: добавление ссылки в таблицу Турниры --- !!!

    return new_spreadsheet_id



def copy_lists(new_spreadsheet_id, source_spreadsheet_id, levelTournament):
# def copy_lists(new_spreadsheet_id, source_spreadsheet_id):
    # Получаем ID исходного листа
    source_sheets_info = service_sheets.spreadsheets().get(spreadsheetId=source_spreadsheet_id).execute()
    source_sheet_id = source_sheets_info['sheets'][0]['properties']['sheetId']  # Первый лист в таблице

    levelTournament_list = list(map(int, levelTournament.split(",")))
    name_division = session.query(Division).all()
    # Создаём словарь {division_id: name}, чтобы быстрее искать названия
    division_dict = {div.division_id: div.name_division for div in name_division}
    # Преобразуем список ID в список названий
    levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]


    # --- Копирование листа -----
    for i in levelTournament_names:
    # for i in range(5):
        # Копируем лист в новую таблицу
        response = service_sheets.spreadsheets().sheets().copyTo(
            spreadsheetId=source_spreadsheet_id,
            sheetId=source_sheet_id,
            body={"destinationSpreadsheetId": new_spreadsheet_id}
        ).execute()

        new_sheet_id = response['sheetId']
        print(f"Лист скопирован! Новый лист ID: {new_sheet_id}")

        # Переименовываем новый лист
        service_sheets.spreadsheets().batchUpdate(
            spreadsheetId=new_spreadsheet_id,
            body={
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": new_sheet_id,
                                "title": f"{i}"
                            },
                            "fields": "title"
                        }
                    }
                ]
            }
        ).execute()

    delete_template_list(new_spreadsheet_id, source_sheet_id)



def accessToSheet(new_spreadsheet_id):
    # --- ДОСТУП К ТАБЛИЦЕ -----
    # Публичный доступ (просмотр)
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service_drive.permissions().create(fileId=new_spreadsheet_id, body=permission).execute()
    link_sheet_tournament = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet_id}"
    print(link_sheet_tournament)

    for email in EMAILS:
        permission_editor = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        time.sleep(1)  # ✅ Пауза в 1 секунду перед отправкой запроса
        service_drive.permissions().create(fileId=new_spreadsheet_id, body=permission_editor).execute()
        print(f"Доступ на редактирование предоставлен: {email}")
    return link_sheet_tournament



def delete_template_list(new_spreadsheet_id, source_sheet_id):
    # Запрос на удаление первого листа
    delete_request = {
        "requests": [
            {
                "deleteSheet": {
                    "sheetId": source_sheet_id
                }
            }
        ]
    }
    service_sheets.spreadsheets().batchUpdate(spreadsheetId=new_spreadsheet_id, body=delete_request).execute()
    print(f"Лист с ID {source_sheet_id} успешно удалён!")



def startDoingSheet(nameTournament, levelTournament):
# def startDoingSheet(nameTournament):
    # ----- Открытие исходной таблицы -----
    gc = gspread.service_account(filename='credentials_tennisbot.json')
    spreadsheet = gc.open("Турнир")
    source_spreadsheet_id = spreadsheet.id

    # ----- Создание новой таблицы турнира -----
    newSheetId = createNewSheet(source_spreadsheet_id, nameTournament)

    # ----- Копирование листов-дивизионов в новой таблице, удаление шаблон-листа из новой таблицы -----
    print("newSheetId = ", newSheetId)
    print("source_spreadsheet_id = ", source_spreadsheet_id)
    print("levelTournament = ", levelTournament)
    copy_lists(newSheetId, source_spreadsheet_id, levelTournament)
    # copy_lists(newSheetId, source_spreadsheet_id)

    # ----- Предоставление доступа к таблице -----
    link_sheet_tournament = accessToSheet(newSheetId)
    return link_sheet_tournament



def addPlayerInList(name, user_link, name_tournament, user_division):
    gc = gspread.service_account(filename='credentials_tennisbot.json')
    spreadsheet = gc.open(name_tournament)
    sheet = spreadsheet.worksheet(user_division)

    user_name = '@' + user_link.replace("https://t.me/", "")

    column_letter = "B"
    values = sheet.col_values(2)  # Получаем все значения из столбца B
    first_empty_row = len(values) + 1  # Находим первую пустую строку

    sheet.update(f"{column_letter}{first_empty_row}", [[f"{name} ({user_name})"]]) # Записываем значение в первую свободную ячейку
    


def edit_name_tournament(old_name_tournament, new_name_tournament):
    # # Создаём клиент Google Drive API
    # drive_service = build("drive", "v3", credentials='credentials_tennisbot.json')
    # sheets_service = build("sheets", "v4", credentials='credentials_tennisbot.json')
   
    drive_service = build("drive", "v3", credentials=creds_drive) # Создаем клиент API Google Drive

    # Ищем таблицу в Google Drive
    query = f"name='{old_name_tournament}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        print(f"❌ Таблица '{old_name_tournament}' не найдена!")
    else:
        spreadsheet_id = files[0]["id"]  # Берем ID первой найденной таблицы

        # Формируем запрос на изменение названия
        update_request = {
            "requests": [
                {
                    "updateSpreadsheetProperties": {
                        "properties": {"title": new_name_tournament},
                        "fields": "title"
                    }
                }
            ]
        }

        # Отправляем запрос в Google Sheets API
        service_sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=update_request).execute()
        print(f"✅ Название таблицы '{old_name_tournament}' изменено на '{new_name_tournament}'!")



def delete_player_from_tournament(nameTournament, person, user_division):
    person = '@' + person.replace("https://t.me/", "")

    # ----- Открытие исходной таблицы -----
    gc = gspread.service_account(filename='credentials_tennisbot.json')
    spreadsheet = gc.open(nameTournament)
    sheet = spreadsheet.worksheet(user_division)
    values = sheet.col_values(2)

    matches = [(i + 1) for i, value in enumerate(values) if person in value]
    if matches:
        # Очистка ячейки с найденным значением
        sheet.update_cell(matches[0], 2, "")  # 2 — это номер колонки (B)
    else:
        print("При удалении из Excel пользователь не был найден!")
