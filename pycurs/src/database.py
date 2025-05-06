import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name='documentation.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Создание таблицы пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_admin BOOLEAN NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Проверяем наличие колонки is_admin
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Если колонки is_admin нет, добавляем её
            if 'is_admin' not in columns:
                # Создаем временную таблицу
                cursor.execute('''
                    CREATE TABLE users_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        is_admin BOOLEAN NOT NULL DEFAULT 0,
                        created_at TIMESTAMP NOT NULL
                    )
                ''')
                
                # Определяем, какие колонки есть в текущей таблице
                if 'created_at' in columns:
                    # Копируем данные, устанавливая is_admin на основе role (если есть)
                    if 'role' in columns:
                        cursor.execute('''
                            INSERT INTO users_temp (id, username, password, is_admin, created_at)
                            SELECT id, username, password, 
                                   CASE WHEN role = 'admin' THEN 1 ELSE 0 END,
                                   created_at
                            FROM users
                        ''')
                    else:
                        cursor.execute('''
                            INSERT INTO users_temp (id, username, password, is_admin, created_at)
                            SELECT id, username, password, 0, created_at FROM users
                        ''')
                else:
                    # Если нет created_at, добавляем текущее время
                    now = datetime.now()
                    if 'role' in columns:
                        cursor.execute('''
                            INSERT INTO users_temp (id, username, password, is_admin, created_at)
                            SELECT id, username, password, 
                                   CASE WHEN role = 'admin' THEN 1 ELSE 0 END,
                                   ?
                            FROM users
                        ''', (now,))
                    else:
                        cursor.execute('''
                            INSERT INTO users_temp (id, username, password, is_admin, created_at)
                            SELECT id, username, password, 0, ? FROM users
                        ''', (now,))
                
                # Удаляем старую таблицу и переименовываем временную
                cursor.execute('DROP TABLE users')
                cursor.execute('ALTER TABLE users_temp RENAME TO users')
            
            # Создание таблицы документов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    created_by INTEGER NOT NULL,
                    doc_type TEXT NOT NULL DEFAULT 'user',
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Проверяем наличие колонки doc_type
            cursor.execute("PRAGMA table_info(documents)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'doc_type' not in columns:
                cursor.execute('ALTER TABLE documents ADD COLUMN doc_type TEXT NOT NULL DEFAULT "user"')
            
            # Создание таблицы версий документов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by INTEGER NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы глоссария
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS glossary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by INTEGER NOT NULL,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы FAQ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faq (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by INTEGER NOT NULL,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы вопросов пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new',
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы оценок разделов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы версий системы
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_number TEXT NOT NULL,
                    description TEXT NOT NULL,
                    changes TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by INTEGER NOT NULL,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Создание таблицы изменений в версиях
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS version_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (version_id) REFERENCES system_versions (id)
                )
            ''')
            
            conn.commit()
            
            # Проверяем, есть ли уже версии системы
            cursor.execute('SELECT COUNT(*) FROM system_versions')
            count = cursor.fetchone()[0]
            
            # Если версий нет, создаем начальную версию
            if count == 0:
                now = datetime.now()
                cursor.execute(
                    '''INSERT INTO system_versions 
                       (version_number, description, changes, created_at, created_by)
                       VALUES (?, ?, ?, ?, ?)''',
                    ('1.0', 'Начальная версия системы', 'Создание системы документации', now, 1)
                )
                conn.commit()

    def add_user(self, username, password, is_admin):
        """Добавляет нового пользователя."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            # Преобразуем is_admin в 1 или 0
            is_admin_int = 1 if is_admin else 0
            cursor.execute(
                '''INSERT INTO users 
                   (username, password, is_admin, created_at)
                   VALUES (?, ?, ?, ?)''',
                (username, password, is_admin_int, now)
            )
            conn.commit()
            return cursor.lastrowid

    def get_user(self, username, password):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ? AND password = ?',
                (username, password)
            )
            return cursor.fetchone()

    def add_document(self, title, content, user_id, doc_type='user'):
        """Добавляет новый документ."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            
            # Создаем документ
            cursor.execute(
                '''INSERT INTO documents 
                   (title, content, created_at, updated_at, created_by, version, doc_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (title, content, now, now, user_id, 1, doc_type)
            )
            doc_id = cursor.lastrowid
            
            # Создаем первую версию
            cursor.execute(
                '''INSERT INTO document_versions 
                   (document_id, content, version, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (doc_id, content, 1, now, user_id)
            )
            
            conn.commit()
            return doc_id

    def update_document(self, doc_id, content, user_id, title=None):
        """Обновляет документ и создает новую версию."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Получаем текущую версию
            cursor.execute('SELECT version FROM documents WHERE id = ?', (doc_id,))
            current_version = cursor.fetchone()[0]
            new_version = current_version + 1
            
            # Обновляем документ
            now = datetime.now()
            if title:
                cursor.execute(
                    '''UPDATE documents 
                       SET content = ?, version = ?, updated_at = ?, title = ?
                       WHERE id = ?''',
                    (content, new_version, now, title, doc_id)
                )
            else:
                cursor.execute(
                    '''UPDATE documents 
                       SET content = ?, version = ?, updated_at = ?
                       WHERE id = ?''',
                    (content, new_version, now, doc_id)
                )
            
            # Сохраняем новую версию
            cursor.execute(
                '''INSERT INTO document_versions 
                   (document_id, content, version, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (doc_id, content, new_version, now, user_id)
            )
            conn.commit()

    def get_document_versions(self, doc_id):
        """Возвращает все версии документа."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT dv.*, u.username 
                   FROM document_versions dv
                   JOIN users u ON u.id = dv.created_by
                   WHERE document_id = ?
                   ORDER BY version DESC''',
                (doc_id,)
            )
            return cursor.fetchall()

    def get_document_version(self, version_id):
        """Возвращает конкретную версию документа."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM document_versions WHERE id = ?''',
                (version_id,)
            )
            return cursor.fetchone()

    def add_glossary_term(self, term, definition, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute(
                '''INSERT INTO glossary 
                   (term, definition, created_at, updated_at, created_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (term, definition, now, now, user_id)
            )
            conn.commit()
            return cursor.lastrowid

    def add_faq(self, question, answer, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute(
                '''INSERT INTO faq 
                   (question, answer, created_at, updated_at, created_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (question, answer, now, now, user_id)
            )
            conn.commit()
            return cursor.lastrowid

    def add_user_question(self, user_id, question):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute(
                '''INSERT INTO user_questions 
                   (user_id, question, status, created_at)
                   VALUES (?, ?, 'new', ?)''',
                (user_id, question, now)
            )
            conn.commit()
            return cursor.lastrowid

    def add_rating(self, document_id, user_id, rating, comment=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute(
                '''INSERT INTO ratings 
                   (document_id, user_id, rating, comment, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (document_id, user_id, rating, comment, now)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_documents(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents ORDER BY title')
            return cursor.fetchall()

    def get_document(self, doc_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
            return cursor.fetchone()

    def get_all_glossary_terms(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM glossary ORDER BY term')
            return cursor.fetchall()

    def get_all_faq(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM faq ORDER BY question')
            return cursor.fetchall()

    def search_documents(self, query):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM documents 
                   WHERE title LIKE ? OR content LIKE ?
                   ORDER BY title''',
                (f'%{query}%', f'%{query}%')
            )
            return cursor.fetchall()

    def get_user_questions(self, status='new'):
        """Получает список вопросов пользователей с указанным статусом."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT user_questions.*, users.username 
                   FROM user_questions 
                   JOIN users ON users.id = user_questions.user_id
                   WHERE status = ?
                   ORDER BY created_at DESC''',
                (status,)
            )
            return cursor.fetchall()

    def get_document_ratings(self, doc_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT r.*, u.username 
                   FROM ratings r
                   JOIN users u ON u.id = r.user_id
                   WHERE document_id = ?
                   ORDER BY created_at DESC''',
                (doc_id,)
            )
            return cursor.fetchall()

    def delete_document(self, doc_id):
        """Удаляет документ и все связанные с ним данные."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Удаляем связанные оценки
            cursor.execute('DELETE FROM ratings WHERE document_id = ?', (doc_id,))
            # Удаляем версии документа
            cursor.execute('DELETE FROM document_versions WHERE document_id = ?', (doc_id,))
            # Удаляем сам документ
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            conn.commit()

    def delete_glossary_term(self, term_id):
        """Удаляет термин из глоссария."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM glossary WHERE id = ?', (term_id,))
            conn.commit()

    def delete_faq(self, faq_id):
        """Удаляет вопрос из FAQ."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM faq WHERE id = ?', (faq_id,))
            conn.commit()

    def delete_user_question(self, question_id):
        """Удаляет вопрос пользователя."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_questions WHERE id = ?', (question_id,))
            conn.commit()

    def add_example_data(self, admin_id):
        """Добавляет примеры документации, терминов и FAQ."""
        # Пример документации
        installation_doc = """# Установка и настройка системы

## Системные требования
- Python 3.9 или выше
- 2 ГБ оперативной памяти
- 500 МБ свободного места на диске

## Шаги установки

1. Клонирование репозитория:
```bash
git clone <url-репозитория>
cd <директория-проекта>
```

2. Создание виртуального окружения:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установка зависимостей:
```bash
pip install -r requirements.txt
```

## Запуск приложения

Для запуска приложения выполните:
```bash
python src/main.py
```

## Первый запуск

1. При первом запуске создайте учетную запись администратора
2. Используйте созданные учетные данные для входа
3. Настройте основные разделы документации
"""
        self.add_document("Установка и настройка", installation_doc, admin_id)

        # Примеры терминов глоссария
        glossary_terms = [
            ("Markdown", "Облегчённый язык разметки для создания форматированного текста."),
            ("PDF", "Portable Document Format, формат файла для представления документов независимо от платформы."),
            ("FAQ", "Frequently Asked Questions (Часто задаваемые вопросы)."),
            ("Версионирование", "Система учета и хранения изменений в документах."),
            ("Экспорт", "Процесс сохранения документа в другом формате.")
        ]
        for term, definition in glossary_terms:
            self.add_glossary_term(term, definition, admin_id)

        # Примеры FAQ
        faqs = [
            ("Как создать новый раздел документации?",
             "Нажмите кнопку \"Добавить раздел\" в левой панели, введите заголовок и содержание раздела, затем нажмите \"Сохранить\"."),
            ("Как экспортировать документацию?",
             "Выберите нужный раздел, нажмите кнопку \"Экспортировать\" и выберите желаемый формат (PDF, HTML или Markdown)."),
            ("Как добавить термин в глоссарий?",
             "Перейдите на вкладку \"Глоссарий\", введите термин и его определение, затем нажмите \"Добавить термин\".")
        ]
        for question, answer in faqs:
            self.add_faq(question, answer, admin_id)

    def get_all_users(self):
        """Возвращает список всех пользователей."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return cursor.fetchall()

    def delete_user(self, user_id):
        """Удаляет пользователя."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()

    def answer_user_question(self, question_id, answer, admin_id):
        """Отвечает на вопрос пользователя и создает новый FAQ."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Получаем вопрос
            cursor.execute(
                'SELECT question, user_id FROM user_questions WHERE id = ?',
                (question_id,)
            )
            question_data = cursor.fetchone()
            
            if question_data:
                question_text = question_data[0]
                user_id = question_data[1]
                
                # Создаем новый FAQ
                now = datetime.now()
                cursor.execute(
                    '''INSERT INTO faq 
                       (question, answer, created_at, created_by)
                       VALUES (?, ?, ?, ?)''',
                    (question_text, answer, now, admin_id)
                )
                
                # Обновляем статус вопроса
                cursor.execute(
                    '''UPDATE user_questions 
                       SET status = 'answered'
                       WHERE id = ?''',
                    (question_id,)
                )
                
                conn.commit()
                return True
            return False

    def get_user_questions_with_answers(self, user_id=None):
        """Получает список вопросов пользователей с ответами."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if user_id:
                # Получаем вопросы конкретного пользователя
                cursor.execute(
                    '''SELECT uq.*, u.username, 
                       (SELECT answer FROM faq WHERE question = uq.question LIMIT 1) as answer
                       FROM user_questions uq
                       JOIN users u ON u.id = uq.user_id
                       WHERE uq.user_id = ?
                       ORDER BY uq.created_at DESC''',
                    (user_id,)
                )
            else:
                # Получаем все вопросы
                cursor.execute(
                    '''SELECT uq.*, u.username, 
                       (SELECT answer FROM faq WHERE question = uq.question LIMIT 1) as answer
                       FROM user_questions uq
                       JOIN users u ON u.id = uq.user_id
                       ORDER BY uq.created_at DESC'''
                )
            return cursor.fetchall()

    def create_new_version(self, version_number, description, changes, user_id):
        """Создает новую версию системы."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            
            # Создаем новую версию
            cursor.execute(
                '''INSERT INTO system_versions 
                   (version_number, description, changes, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?)''',
                (version_number, description, changes, now, user_id)
            )
            version_id = cursor.lastrowid
            
            conn.commit()
            return version_id

    def add_version_change(self, version_id, change_type, entity_type, entity_id, description):
        """Добавляет запись об изменении в версии."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute(
                '''INSERT INTO version_changes 
                   (version_id, change_type, entity_type, entity_id, description, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (version_id, change_type, entity_type, entity_id, description, now)
            )
            conn.commit()

    def get_latest_version(self):
        """Возвращает последнюю версию системы."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT sv.*, u.username 
                   FROM system_versions sv
                   JOIN users u ON u.id = sv.created_by
                   ORDER BY sv.id DESC
                   LIMIT 1'''
            )
            return cursor.fetchone()

    def get_version_changes(self, version_id):
        """Возвращает все изменения для указанной версии."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM version_changes 
                   WHERE version_id = ?
                   ORDER BY created_at''',
                (version_id,)
            )
            return cursor.fetchall()

    def get_all_versions(self):
        """Возвращает список всех версий системы с изменениями."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT sv.*, u.username,
                   (SELECT GROUP_CONCAT(description, '; ')
                    FROM version_changes
                    WHERE version_id = sv.id) as changes
                   FROM system_versions sv
                   JOIN users u ON u.id = sv.created_by
                   ORDER BY sv.id DESC'''
            )
            return cursor.fetchall()

    def delete_version(self, version_id):
        """Удаляет версию системы и связанные с ней изменения."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Удаляем связанные изменения
            cursor.execute('DELETE FROM version_changes WHERE version_id = ?', (version_id,))
            # Удаляем саму версию
            cursor.execute('DELETE FROM system_versions WHERE id = ?', (version_id,))
            conn.commit()

    def get_document_versions(self, doc_id):
        """Возвращает все версии документа."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT dv.*, u.username 
                   FROM document_versions dv
                   JOIN users u ON u.id = dv.created_by
                   WHERE document_id = ?
                   ORDER BY version DESC''',
                (doc_id,)
            )
            return cursor.fetchall()

    def delete_document_version(self, version_id):
        """Удаляет версию документа."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM document_versions WHERE id = ?', (version_id,))
            conn.commit()

    def update_glossary_term(self, term_id, term, definition):
        """Обновляет термин глоссария."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE glossary SET term = ?, definition = ? WHERE id = ?',
                (term, definition, term_id)
            )
            conn.commit()
            
    def update_faq(self, faq_id, question, answer):
        """Обновляет вопрос-ответ в FAQ."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE faq SET question = ?, answer = ? WHERE id = ?',
                (question, answer, faq_id)
            )
            conn.commit()
            
    def get_glossary_term(self, term_id):
        """Возвращает термин глоссария по ID."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM glossary WHERE id = ?', (term_id,))
            return cursor.fetchone()
            
    def get_faq(self, faq_id):
        """Возвращает вопрос-ответ из FAQ по ID."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM faq WHERE id = ?', (faq_id,))
            return cursor.fetchone()

    def restore_system_to_version(self, version_id):
        """Восстанавливает систему до указанной версии."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Получаем информацию о версии
            cursor.execute(
                'SELECT * FROM system_versions WHERE id = ?',
                (version_id,)
            )
            version = cursor.fetchone()
            
            if not version:
                return False
            
            # Получаем все документы
            cursor.execute('SELECT id FROM documents')
            all_documents = cursor.fetchall()
            
            # Для каждого документа находим его состояние на момент указанной версии
            for doc in all_documents:
                doc_id = doc[0]
                
                # Находим версию документа, которая была актуальна на момент указанной версии системы
                cursor.execute(
                    '''SELECT * FROM document_versions 
                       WHERE document_id = ? AND created_at <= ?
                       ORDER BY version DESC 
                       LIMIT 1''',
                    (doc_id, version[4])  # version[4] - created_at
                )
                doc_version = cursor.fetchone()
                
                if doc_version:
                    # Обновляем документ до этой версии
                    cursor.execute(
                        '''UPDATE documents 
                           SET content = ?, updated_at = ? 
                           WHERE id = ?''',
                        (doc_version[2], datetime.now(), doc_id)
                    )
            
            # Также можно восстановить удаленные документы, если у нас есть их версии
            # Получаем все версии документов
            cursor.execute(
                '''SELECT DISTINCT document_id FROM document_versions 
                   WHERE created_at <= ?''',
                (version[4],)
            )
            all_versioned_docs = cursor.fetchall()
            
            # Проверяем, есть ли документы, которые были удалены
            for doc in all_versioned_docs:
                doc_id = doc[0]
                
                # Проверяем, существует ли документ сейчас
                cursor.execute('SELECT id FROM documents WHERE id = ?', (doc_id,))
                if not cursor.fetchone():
                    # Если документа нет, восстанавливаем его из последней версии до указанной версии системы
                    cursor.execute(
                        '''SELECT * FROM document_versions 
                           WHERE document_id = ? AND created_at <= ?
                           ORDER BY version DESC 
                           LIMIT 1''',
                        (doc_id, version[4])
                    )
                    doc_version = cursor.fetchone()
                    
                    if doc_version:
                        # Получаем информацию о документе из его версии
                        # Так как документ удален, мы не можем получить его title и doc_type из таблицы documents
                        # Поэтому используем информацию из версии
                        now = datetime.now()
                        
                        # Восстанавливаем документ с базовой информацией
                        cursor.execute(
                            '''INSERT INTO documents 
                               (id, title, content, version, created_at, updated_at, created_by, doc_type)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (doc_id, f"Восстановленный документ {doc_id}", doc_version[2], doc_version[3], 
                             doc_version[4], now, doc_version[5], 'user')
                        )
            
            conn.commit()
            return True 