# Локальный запуск бота и Mini App на Windows

Бот работает с вашего компьютера, а Telegram открывает Mini App через временный HTTPS-адрес (туннель).
Все команды вводятся в **PowerShell** (Пуск → «PowerShell»).

---

## 1. Установить программы

Проще всего через `winget` (встроен в Windows 10/11):

```powershell
winget install Python.Python.3.12
winget install Git.Git
winget install Cloudflare.cloudflared
winget install Oracle.MySQL
```

- Для **MySQL** надёжнее официальный установщик **MySQL Installer** (dev.mysql.com → MySQL Installer for Windows):
  выберите «Server only» или «Full», если нужен MySQL Workbench. Задайте пароль для `root` и запомните его.
- После установки **закройте и снова откройте PowerShell**, чтобы новые команды стали доступны.
- Проверка: `python --version`, `git --version`, `cloudflared --version`.

---

## 2. Скачать код и поставить библиотеки

```powershell
cd $HOME\Desktop
git clone https://github.com/Pahapo/Tennis_bot.git
cd Tennis_bot
git checkout claude/confident-babbage-72mn4e

python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Если `Activate.ps1` пишет, что «выполнение сценариев отключено», один раз выполните:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

и повторите активацию. В начале строки должно появиться `(venv)`.

---

## 3. База данных

В PowerShell команда `mysql ... < файл.sql` не работает, поэтому есть два способа.

### Способ А — MySQL Workbench (проще)

1. Подключитесь к локальному серверу под `root`.
2. Выполните:
   ```sql
   CREATE DATABASE tennis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Выберите базу `tennis` (двойной клик слева) → File → **Run SQL Script** → `tennisDB_script.sql` из папки проекта.

### Способ Б — командная строка

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "CREATE DATABASE tennis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p --default-character-set=utf8mb4 tennis -e "source tennisDB_script.sql"
```

### Копия рабочей базы

Если хотите работать с копией рабочей базы: сначала залейте её дамп, затем тем же способом выполните
**`update_miniapp.sql`** (вместо `tennisDB_script.sql`). Так заодно проверите обновление до запуска на сервере.

> `update_miniapp.sql` — все изменения базы для Mini App. На рабочем сервере его нужно выполнить **один раз**,
> **до** запуска новой версии бота (лучше после резервной копии базы).

### Проверка базы

Если база создана давно (по старой схеме), в ней может не хватать таблиц или колонок —
тогда бот пишет ошибки вида `Unknown column ...` или `Table ... doesn't exist`. Проверьте базу скриптом
(из папки `Tennis_bot`, с активированным `venv`):

```powershell
python check_db.py          # показать, чего не хватает
python check_db.py --fix    # добавить недостающие таблицы и колонки (данные не трогает)
```

---

## 4. Файлы в папке `Tennis_bot` (рядом с `requirements.txt`)

- **`credentials_tennisbot.json`** — ключ Google-таблиц, скопируйте с сервера.
  Без него бот не стартует (`googleSheet.py` читает его сразу при запуске).
- **`.env`** — создайте Блокнотом: «Сохранить как» → тип «Все файлы» → имя `.env` → кодировка UTF-8.

```
TOKEN=токен_бота
DATABASE_URL=mysql+aiomysql://root:ВАШ_ПАРОЛЬ@localhost:3306/tennis?charset=utf8mb4
WEBAPP_URL=https://адрес-из-шага-5
WEBAPP_PORT=8080
# ADMIN_CHAT=id_чата_админов     (необязательно: споры по счёту и модерация барахолки)
```

Остальные переменные — как на сервере: `BOT_USERNAME`, `CHANNEL`, `CHANNEL_CHAT`, `CHANNELS_SUB`,
`CHANNEL_SCORES`, `ADMINS`, `MAIN_EDITOR`, `EDITOR`, `DIVISION_EDITOR`, `EMAILS`. Без них бот упадёт при старте.

---

## 5. Запуск (два окна PowerShell)

### Окно 1 — туннель

```powershell
cloudflared tunnel --url http://localhost:8080
```

Найдите в выводе строку `https://....trycloudflare.com`, скопируйте её в `WEBAPP_URL` в `.env` и сохраните.
Окно не закрывайте.

### Окно 2 — бот

```powershell
cd $HOME\Desktop\Tennis_bot
venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
python Tennis\main.py
```

- `PYTHONUTF8` — чтобы эмодзи в сообщениях консоли не вызывали ошибок кодировки.
- Запускать нужно **из папки `Tennis_bot`**, не из `Tennis`: от неё считаются пути к картинкам.
- При успешном запуске появится `Mini App запущен на порту 8080`.
  Откройте бота в Telegram: слева от поля ввода будет кнопка «Приложение», после `/start` — «🎾 Открыть приложение».

---

## Важно

- **Один токен — одна копия бота.** Пока рабочий бот выключен, можно запускать локально с его токеном.
  Если он работает на сервере — для разработки создайте тестового бота в @BotFather (`/newbot`).
- **Адрес туннеля меняется** при каждом запуске `cloudflared`. После перезапуска туннеля обновите `WEBAPP_URL`
  в `.env` и перезапустите бота — он сам переставит кнопку «Приложение» на новый адрес.
- **Компьютер должен быть включён**, пока вы проверяете — бот и приложение работают с него.
- **Отладка** удобнее всего в Telegram Desktop. Ошибки сервера печатаются в окне с ботом.

---

## Если что-то не так

| Ошибка | Что делать |
|---|---|
| `Can't connect to MySQL server` | MySQL не запущен (Пуск → «Службы» → MySQL80 → Запустить) или неверный пароль в `DATABASE_URL` |
| `No such file ... credentials_tennisbot.json` | файл не лежит в `Tennis_bot` или бот запущен не из этой папки |
| `AttributeError: 'NoneType' object has no attribute 'split'` | в `.env` не хватает одной из переменных (`CHANNELS_SUB`, `ADMINS` и т. п.) |
| `Conflict: terminated by other getUpdates request` | этот токен уже запущен где-то ещё — остановите другую копию или возьмите тестового бота |
| Приложение не открывается | закрыто окно с `cloudflared` или в `WEBAPP_URL` старый адрес (он меняется при каждом запуске туннеля) — обновите и перезапустите бота |
| Windows спрашивает про брандмауэр | разрешите доступ для Python |
