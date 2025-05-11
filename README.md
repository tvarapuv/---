Что то типа плана:
Шаг 1. Рефакторинг существующей базы кода
1.1. Разнести проект по модулям (db.py, ui_student.py, ui_teacher.py, adaptive.py, reports.py).
1.2. Вычистить прямое обращение GUI → SQLite: все запросы в слой repository.py.
1.3. Завести единый файл настроек config.py (пути к БД, пороги адаптации, роли).

Шаг 2. Расширение схемы SQLite под учебный процесс
-- Описания сущностей
CREATE TABLE student( id INTEGER PRIMARY KEY, fio TEXT, group_id INT );
CREATE TABLE teacher( id INTEGER PRIMARY KEY, fio TEXT );

CREATE TABLE course( id INTEGER PRIMARY KEY, name TEXT, teacher_id INT );
CREATE TABLE module( id INTEGER PRIMARY KEY, course_id INT, title TEXT, level INT );      -- level = «сложность»
CREATE TABLE resource(
    id INTEGER PRIMARY KEY,
    module_id INT,
    title TEXT,
    type TEXT,                      -- ‘lecture’, ‘test’, ‘video’, ‘guide’
    difficulty INT DEFAULT 1        -- условный показатель сложности
);

-- Прогресс и оценки
CREATE TABLE progress(
    id INTEGER PRIMARY KEY,
    student_id INT,
    module_id INT,
    score REAL,                     -- 0‑100 %
    attempts INT DEFAULT 1,
    updated_at DATETIME
);

-- Правила/пороги адаптации
CREATE TABLE adapt_threshold(
    id INTEGER PRIMARY KEY,
    min_score INT,                  -- напр. 0‑60
    resource_type TEXT,             -- ‘guide’ / ‘video’
    action TEXT                     -- что подсовываем
);
Seed‑скрипт: вставить пару правил: при score < 60 % выдаём «дополнительный разбор»; при 60–80 % — «закрепляющее видео», и т.п.

Шаг 3. Модуль адаптивной логики adaptive.py
3.1. analyze_progress(student_id)
Находит модули с низким баллом → выбирает подходящий ресурс по таблице adapt_threshold и сложности.
3.2. get_recommendations(student_id)
Возвращает JSON список [{module, resource_id, reason}].
3.3. update_after_attempt(student_id, module_id, new_score)
Записывает в progress, пересчитывает рекомендации.

Шаг 4. Изменения GUI (Tkinter/PyQt – как в курсовой)
4.1. Роль «Студент»
Экран «Мои курсы» – таблица модулей + текущий балл.
Кнопка «Рекомендовано» – открывает список из adaptive.get_recommendations().
Просмотр ресурса – открывает PDF/ссылку/тест внутри WebView.

4.2. Роль «Преподаватель»
Экран «Курсы» – CRUD модулей и ресурсов.
Экран «Аналитика» – график среднего балла по каждому модулю (используем matplotlib).
Настройка порогов адаптации – форма редактирования adapt_threshold.
4.3. Роль «Администратор»
Управление пользователями и резервное копирование БД (кнопка «Backup to zip»).

Шаг 5. Справочная система (help‑центр)
5.1. Таблица help_article(id, audience TEXT, title, body_md).
5.2. В студенческом UI – раздел «Справка» с фильтром по audience='student'.
5.3. В учительском UI – «Методические материалы» (audience='teacher').
5.4. CRUD статей – доступен преподавателю (или админу).

Шаг 6. Отчётность и визуализация
6.1. reports.py – функции формирования CSV/Excel с успеваемостью.
6.2. Графики:
plt.plot(mod_names, avg_scores)      # средний балл
plt.barh(students, debt_count)       # долги по модулям
6.3. Экспорт отчёта в PDF (reportlab) для печати.

Шаг 7. Безопасность и устойчивость
7.1. Пароли → bcrypt.
7.2. Автовход отключён; сессия хранится в памяти, тайм‑аут 30 мин.
7.3. Ежедневный авто‑backup — sqlite3 .dump | gzip (cron/TaskScheduler).

Шаг 8. Тесты
unit: pytest для adaptive.py (правильный выбор ресурса).
integration: сценарий «студент проходит тест → рекомендация меняется».
GUI smoke: pytest-qt или pytest-tkinter – открытие главных окон без ошибок.

Шаг 9. Сценарий демонстрации
Запустить main.py – меню входа.
Войти как Teacher → создать курс «Python Basics», добавить 2 модуля и ресурсы разных уровней.
Войти как Student → пройти короткий тест с низким баллом → нажать «Рекомендовано» → увидеть дополнительный материал.
Teacher открывает «Аналитику» → график успеваемости обновлён.
Teacher создает/редактирует статью справки «Как пересдать модуль».
Student в разделе «Справка» открывает новую статью.
Teacher экспортирует отчёт PDF и делает резервную копию БД.
