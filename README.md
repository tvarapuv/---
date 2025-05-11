Так, не вдаваясь в техничку - оставляем ядро курсовой, добавляем БД для клиентов/заказов, тонкий API, мобильный «фронт» и лёгкую справочную систему. Реальное кодирование — это CRUD + два‑три экрана в React Native; безопасность ограничивается JWT, HTTPS и лимитом попыток. Этого достаточно, чтобы на защите показать «одна база → два клиента (ПК и мобильный) → встроенная справка».

Что то типа плана:
Шаг 1. Вычистить и упорядочить исходники курсовой
1.1. Вынести логику из tkinter‑окон в отдельные файлы
  db.py — все функции работы c SQLite
  auth.py — регистрация/вход, хеш‑пароли (bcrypt)
  models.py — ORM‑класс User, Log
1.2. Переименовать GUI‑файлы (например admin_ui.py, user_ui.py) и оставить там только код интерфейса.

Шаг 2. Расширить базу данных для «клиентов + заказы + справка»
2.1. Добавить таблицы
CREATE TABLE client(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "order"(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER REFERENCES client(id),
    status TEXT DEFAULT 'new',
    total REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE faq(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT,
    question TEXT,
    answer TEXT
);
2.2. В db.py добавить CRUD‑функции add_client(), list_orders() и т.д.

Шаг 3. Сделать тонкий REST‑слой (Flask / FastAPI)
3.1. Создать api.py:
app = FastAPI()

@app.post("/login")          # возвращает JWT
@app.get ("/clients")        
@app.post("/orders")         
@app.get ("/faq")            
3.2. Авторизация по JWT токену: fastapi-jwt-auth или pyjwt; хранить токен 2 ч, рефреш – сутки.
3.3. Встроить CORS для мобильного клиента.

Шаг 4. Переключить десктоп‑GUI на API
4.1. В GUI‑файлах заменить прямые запросы к SQLite на HTTP requests к localhost:8000.
4.2. Администраторский функционал (добавление пользователей, просмотр логов) оставить локально — это «консоль админа».

Шаг 5. Мини‑справочная система
5.1. Файл help_loader.py — заполняет таблицу faq из Markdown‑директории.
5.2. В GUI и в API сделать эндпоинт /faq?section=orders и кнопку «Справка».

Шаг 6. Простейший мобильный клиент
6.1. Самый быстрый путь — React Native + Expo.
Экраны:
LoginScreen (POST /login)
ClientsScreen (GET /clients)
OrdersScreen (GET /orders)
HelpScreen (GET /faq)
6.2. Собрать через expo build:android → apk; этого хватит для демонстрации.

Шаг 7. Безопасность + DevOps
7.1. Запуск API за gunicorn + UvicornWorker → проксируем через Nginx c самоподписанным SSL.
7.2. Limiter (slowapi) — 5 запросов логина в минуту.
7.3. Сценарий резервного копирования: sqlite3 dump | gzip > backup.sql.gz, cron каждые 24 ч.
7.4. Логирование: loguru → файл app.log; в десктоп‑GUI показать логи администратору.

Шаг 8. Тесты
8.1. Unit: pytest для функций в db.py.
8.2. API: pytest + httpx (проверить /login, /clients, /faq).
8.3. Нагрузочный скрипт: locust или k6 run — 50 пользователей, 5 минут.

Шаг 9. Упаковка и демонстрация
9.1. Скрипт run_desktop.bat / .sh запускает API, потом GUI.
9.2. Типа демонстрация:
  – логин админа → создание клиента
  – запуск мобильного приложения (Android эмулятор) → тот же клиент отображается
  – кнопка «Справка» открывает FAQ
