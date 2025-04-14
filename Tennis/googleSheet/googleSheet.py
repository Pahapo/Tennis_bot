import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


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

# def copy_lists(new_spreadsheet_id, source_spreadsheet_id, levelTournament):
def copy_lists(new_spreadsheet_id, source_spreadsheet_id):
    # Получаем ID исходного листа
    source_sheets_info = service_sheets.spreadsheets().get(spreadsheetId=source_spreadsheet_id).execute()
    source_sheet_id = source_sheets_info['sheets'][0]['properties']['sheetId']  # Первый лист в таблице

    # --- Копирование листа -----
    # for i in levelTournament:
    for i in range(5):
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
                                "title": f"Дивизион {i}"
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
    print(f"Таблица теперь доступна всем по ссылке: https://docs.google.com/spreadsheets/d/{new_spreadsheet_id}")

    # Доступ на редактирование для определённых пользователей
    EMAILS = ['goovelshop@gmail.com']
    for email in EMAILS:
        permission_editor = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        service_drive.permissions().create(fileId=new_spreadsheet_id, body=permission_editor).execute()
        print(f"Доступ на редактирование предоставлен: {email}")

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

# def startDoingSheet(nameTournament, levelTournament):
def startDoingSheet(nameTournament):
    # ----- Открытие исходной таблицы -----
    gc = gspread.service_account(filename='credentials_tennisbot.json')
    spreadsheet = gc.open("Турнир")
    source_spreadsheet_id = spreadsheet.id

    # ----- Создание новой таблицы турнира -----
    newSheetId = createNewSheet(source_spreadsheet_id, nameTournament)

    # ----- Копирование листов-дивизионов в новой таблице, удаление шаблон-листа из новой таблицы -----
    # copy_lists(newSheetId, source_spreadsheet_id, levelTournament)
    copy_lists(newSheetId, source_spreadsheet_id)

    # ----- Предоставление доступа к таблице -----
    accessToSheet(newSheetId)




