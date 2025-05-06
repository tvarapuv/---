from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QTextEdit, QPushButton, QListWidget, QTabWidget,
                           QLineEdit, QMessageBox, QSpinBox, QFileDialog, QComboBox, QGroupBox,
                           QDialog, QDialogButtonBox, QCheckBox, QListWidgetItem)
from PyQt6.QtCore import Qt
import markdown
from utils import export_to_pdf, export_to_html, export_to_markdown
import os
import shutil

class AdminWindow(QMainWindow):
    def __init__(self, db, user_id, main_window=None):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()
        
        # Левая панель с разделами
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        sections_label = QLabel('Разделы документации')
        self.sections_list = QListWidget()
        self.sections_list.itemClicked.connect(self.load_document)
        
        buttons_layout = QHBoxLayout()
        add_section_btn = QPushButton('Добавить раздел')
        add_section_btn.clicked.connect(self.add_section)
        delete_section_btn = QPushButton('Удалить раздел')
        delete_section_btn.setStyleSheet('background-color: #ff6b6b; color: white;')
        delete_section_btn.clicked.connect(self.delete_section)
        buttons_layout.addWidget(add_section_btn)
        buttons_layout.addWidget(delete_section_btn)
        
        # Добавляем кнопку выхода
        logout_btn = QPushButton('Выйти из системы')
        logout_btn.setStyleSheet('background-color: #ff6b6b; color: white; padding: 5px;')
        logout_btn.clicked.connect(self.logout)
        
        left_layout.addWidget(sections_label)
        left_layout.addWidget(self.sections_list)
        left_layout.addLayout(buttons_layout)
        left_layout.addStretch()
        left_layout.addWidget(logout_btn)
        left_panel.setLayout(left_layout)
        
        # Правая панель с табами
        right_panel = QTabWidget()
        
        # Таб редактирования документации
        doc_tab = QWidget()
        doc_layout = QVBoxLayout()
        
        self.doc_title = QLineEdit()
        self.doc_title.setPlaceholderText('Заголовок раздела')
        
        # Добавляем выбор типа документации
        doc_type_layout = QHBoxLayout()
        doc_type_label = QLabel('Тип документации:')
        self.doc_type_combo = QComboBox()
        self.doc_type_combo.addItems(['Руководство пользователя', 'Руководство администратора'])
        doc_type_layout.addWidget(doc_type_label)
        doc_type_layout.addWidget(self.doc_type_combo)
        
        self.doc_content = QTextEdit()
        self.doc_content.setPlaceholderText('Содержание раздела (поддерживается Markdown)')
        
        # Добавляем кнопку для вставки изображений
        image_btn = QPushButton('Вставить изображение')
        image_btn.clicked.connect(self.insert_image)
        
        # Добавляем список версий документа
        versions_group = QGroupBox('Версии документа')
        versions_layout = QVBoxLayout()
        self.doc_versions_list = QListWidget()
        self.doc_versions_list.itemDoubleClicked.connect(self.restore_doc_version)
        
        # Кнопки управления версиями документа
        doc_versions_buttons = QHBoxLayout()
        view_version_btn = QPushButton('Просмотреть')
        view_version_btn.clicked.connect(self.view_doc_version)
        restore_version_btn = QPushButton('Восстановить')
        restore_version_btn.clicked.connect(self.restore_doc_version)
        delete_version_btn = QPushButton('Удалить')
        delete_version_btn.setStyleSheet('background-color: #ff6b6b; color: white;')
        delete_version_btn.clicked.connect(self.delete_doc_version)
        
        doc_versions_buttons.addWidget(view_version_btn)
        doc_versions_buttons.addWidget(restore_version_btn)
        doc_versions_buttons.addWidget(delete_version_btn)
        
        versions_layout.addWidget(self.doc_versions_list)
        versions_layout.addLayout(doc_versions_buttons)
        versions_group.setLayout(versions_layout)
        
        # Добавляем группу для отображения оценок
        ratings_group = QGroupBox('Оценки пользователей')
        ratings_layout = QVBoxLayout()
        self.ratings_list = QListWidget()
        ratings_layout.addWidget(self.ratings_list)
        ratings_group.setLayout(ratings_layout)
        
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton('Сохранить')
        save_btn.clicked.connect(self.save_document)
        export_btn = QPushButton('Экспортировать')
        export_btn.clicked.connect(self.export_document)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(image_btn)
        
        doc_layout.addLayout(doc_type_layout)
        doc_layout.addWidget(self.doc_title)
        doc_layout.addWidget(self.doc_content)
        doc_layout.addWidget(versions_group)
        doc_layout.addWidget(ratings_group)
        doc_layout.addLayout(buttons_layout)
        doc_tab.setLayout(doc_layout)
        
        # Таб управления пользователями
        users_tab = QWidget()
        users_layout = QVBoxLayout()
        
        # Список пользователей
        users_group = QGroupBox('Пользователи')
        users_list_layout = QVBoxLayout()
        self.users_list = QListWidget()
        
        users_buttons_layout = QHBoxLayout()
        add_user_btn = QPushButton('Добавить пользователя')
        add_user_btn.clicked.connect(self.add_user)
        delete_user_btn = QPushButton('Удалить пользователя')
        delete_user_btn.setStyleSheet('background-color: #ff6b6b; color: white;')
        delete_user_btn.clicked.connect(self.delete_user)
        users_buttons_layout.addWidget(add_user_btn)
        users_buttons_layout.addWidget(delete_user_btn)
        
        users_list_layout.addWidget(self.users_list)
        users_list_layout.addLayout(users_buttons_layout)
        users_group.setLayout(users_list_layout)
        users_layout.addWidget(users_group)
        users_tab.setLayout(users_layout)
        
        # Таб глоссария
        glossary_tab = self.create_glossary_tab()
        
        # Таб FAQ
        faq_tab = QWidget()
        faq_layout = QVBoxLayout()
        
        # Поля для ввода FAQ
        faq_input_group = QGroupBox('Добавить новый FAQ')
        faq_input_layout = QVBoxLayout()
        
        question_label = QLabel('Вопрос:')
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText('Введите вопрос')
        
        answer_label = QLabel('Ответ:')
        self.answer_input = QTextEdit()
        self.answer_input.setPlaceholderText('Введите ответ')
        
        faq_buttons_layout = QHBoxLayout()
        add_faq_btn = QPushButton('Добавить FAQ')
        add_faq_btn.clicked.connect(self.add_faq)
        edit_faq_btn = QPushButton('Редактировать')
        edit_faq_btn.clicked.connect(self.edit_faq)
        delete_faq_btn = QPushButton('Удалить FAQ')
        delete_faq_btn.setStyleSheet('background-color: #ff6b6b; color: white;')
        delete_faq_btn.clicked.connect(self.delete_faq)
        faq_buttons_layout.addWidget(add_faq_btn)
        faq_buttons_layout.addWidget(edit_faq_btn)
        faq_buttons_layout.addWidget(delete_faq_btn)
        
        faq_input_layout.addWidget(question_label)
        faq_input_layout.addWidget(self.question_input)
        faq_input_layout.addWidget(answer_label)
        faq_input_layout.addWidget(self.answer_input)
        faq_input_layout.addLayout(faq_buttons_layout)
        faq_input_group.setLayout(faq_input_layout)
        
        # Список FAQ
        faq_list_group = QGroupBox('Список FAQ')
        faq_list_layout = QVBoxLayout()
        self.faq_list = QListWidget()
        self.faq_list.itemClicked.connect(self.show_faq)
        faq_list_layout.addWidget(self.faq_list)
        faq_list_group.setLayout(faq_list_layout)
        
        faq_layout.addWidget(faq_input_group)
        faq_layout.addWidget(faq_list_group)
        faq_tab.setLayout(faq_layout)
        
        # Таб вопросов пользователей
        questions_tab = QWidget()
        questions_layout = QVBoxLayout()
        
        # Список вопросов
        questions_group = QGroupBox('Вопросы пользователей')
        questions_list_layout = QVBoxLayout()
        self.questions_list = QListWidget()
        self.questions_list.itemClicked.connect(self.show_question_details)
        
        # Поле для ответа
        answer_group = QGroupBox('Ответ на вопрос')
        answer_layout = QVBoxLayout()
        self.question_answer_input = QTextEdit()
        self.question_answer_input.setPlaceholderText('Введите ответ на вопрос...')
        
        answer_buttons_layout = QHBoxLayout()
        answer_btn = QPushButton('Ответить')
        answer_btn.clicked.connect(self.answer_question)
        delete_question_btn = QPushButton('Удалить вопрос')
        delete_question_btn.setStyleSheet('background-color: #ff6b6b; color: white;')
        delete_question_btn.clicked.connect(self.delete_user_question)
        answer_buttons_layout.addWidget(answer_btn)
        answer_buttons_layout.addWidget(delete_question_btn)
        
        answer_layout.addWidget(self.question_answer_input)
        answer_layout.addLayout(answer_buttons_layout)
        answer_group.setLayout(answer_layout)
        
        questions_list_layout.addWidget(self.questions_list)
        questions_group.setLayout(questions_list_layout)
        
        questions_layout.addWidget(questions_group)
        questions_layout.addWidget(answer_group)
        questions_tab.setLayout(questions_layout)
        
        # Таб версий системы
        versions_tab = QWidget()
        versions_layout = QVBoxLayout()
        
        # Список версий
        versions_group = QGroupBox('Версии системы')
        versions_list_layout = QVBoxLayout()
        self.versions_list = QListWidget()
        self.versions_list.itemClicked.connect(self.show_version_details)
        
        # Кнопки управления версиями системы
        versions_buttons = QHBoxLayout()
        restore_sys_version_btn = QPushButton('Восстановить до этой версии')
        restore_sys_version_btn.clicked.connect(self.restore_system_version)
        delete_sys_version_btn = QPushButton('Удалить версию')
        delete_sys_version_btn.setStyleSheet('background-color: #ff6b6b; color: white;')
        delete_sys_version_btn.clicked.connect(self.delete_system_version)
        versions_buttons.addWidget(restore_sys_version_btn)
        versions_buttons.addWidget(delete_sys_version_btn)
        
        # Детали версии
        version_details_group = QGroupBox('Детали версии')
        version_details_layout = QVBoxLayout()
        
        self.version_details = QTextEdit()
        self.version_details.setReadOnly(True)
        
        version_details_layout.addWidget(self.version_details)
        version_details_group.setLayout(version_details_layout)
        
        versions_list_layout.addWidget(self.versions_list)
        versions_list_layout.addLayout(versions_buttons)
        versions_group.setLayout(versions_list_layout)
        
        versions_layout.addWidget(versions_group)
        versions_layout.addWidget(version_details_group)
        versions_tab.setLayout(versions_layout)
        
        # Добавляем все табы
        right_panel.addTab(doc_tab, "Документация")
        right_panel.addTab(users_tab, "Пользователи")
        right_panel.addTab(glossary_tab, "Глоссарий")
        right_panel.addTab(faq_tab, "FAQ")
        right_panel.addTab(questions_tab, "Вопросы")
        right_panel.addTab(versions_tab, "Версии")
        
        # Добавляем панели в главный layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.setWindowTitle('Панель администратора')
        self.setGeometry(100, 100, 1200, 800)
        
        # Загружаем данные
        self.load_data()

    def load_data(self):
        # Загружаем документы
        documents = self.db.get_all_documents()
        self.sections_list.clear()
        for doc in documents:
            self.sections_list.addItem(doc[1])  # doc[1] - title
            
        # Загружаем термины глоссария
        terms = self.db.get_all_glossary_terms()
        self.glossary_list.clear()
        for term in terms:
            self.glossary_list.addItem(f"{term[1]}: {term[2]}")  # term[1] - term name, term[2] - definition
            
        # Загружаем FAQ
        faqs = self.db.get_all_faq()
        self.faq_list.clear()
        for faq in faqs:
            item = QListWidgetItem(f"Q: {faq[1]}\nA: {faq[2]}")  # faq[1] - question, faq[2] - answer
            item.setData(Qt.ItemDataRole.UserRole, faq[0])  # faq[0] - id
            self.faq_list.addItem(item)
            
        # Загружаем вопросы пользователей с ответами
        questions = self.db.get_user_questions_with_answers()
        self.questions_list.clear()
        for q in questions:
            status = '[Отвечен]' if q[3] == 'answered' else '[Новый]'
            self.questions_list.addItem(f"{status} От {q[5]}: {q[2]}")  # q[5] - username, q[2] - question

        # Загружаем список пользователей
        try:
            users = self.db.get_all_users()
            self.users_list.clear()
            for user in users:
                # Проверяем, является ли пользователь админом
                is_admin = bool(user[3])  # Преобразуем в булево значение
                item = QListWidgetItem(f"{user[1]} ({'Админ' if is_admin else 'Пользователь'})")
                item.setData(Qt.ItemDataRole.UserRole, user[0])  # Сохраняем ID пользователя
                self.users_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке пользователей: {str(e)}')

        # Загружаем версии системы
        try:
            versions = self.db.get_all_versions()
            self.versions_list.clear()
            for version in versions:
                item = QListWidgetItem(f"Версия {version[1]} ({version[6]})")  # version[1] - number, version[6] - username
                item.setData(Qt.ItemDataRole.UserRole, version[0])  # version[0] - id
                self.versions_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке версий: {str(e)}')

        # Загружаем версии документа, если выбран документ
        if hasattr(self, 'current_doc_id'):
            try:
                doc_versions = self.db.get_document_versions(self.current_doc_id)
                self.doc_versions_list.clear()
                for version in doc_versions:
                    item = QListWidgetItem(f"Версия {version[3]} ({version[6]}) - {version[4]}")  # version[3] - version, version[6] - username, version[4] - date
                    item.setData(Qt.ItemDataRole.UserRole, version[0])  # version[0] - id
                    self.doc_versions_list.addItem(item)
                
                # Загружаем оценки документа
                self.load_document_ratings(self.current_doc_id)
                
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке версий документа: {str(e)}')

    def add_section(self):
        if not self.doc_title.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите заголовок раздела')
            return
            
        try:
            # Определяем тип документации
            doc_type = 'admin' if self.doc_type_combo.currentText() == 'Руководство администратора' else 'user'
            
            doc_id = self.db.add_document(
                self.doc_title.text(),
                self.doc_content.toPlainText(),
                self.user_id,
                doc_type
            )
            self.sections_list.addItem(self.doc_title.text())
            
            # Создаем новую версию системы
            version_id = self.create_new_version(
                f"Добавлен новый раздел: {self.doc_title.text()}",
                f"Добавлен новый раздел документации типа {self.doc_type_combo.currentText()}"
            )
            
            if version_id:
                self.db.add_version_change(
                    version_id,
                    'add',
                    'document',
                    doc_id,
                    f"Добавлен раздел '{self.doc_title.text()}'"
                )
            
            QMessageBox.information(self, 'Успех', 'Раздел добавлен')
            self.doc_title.clear()
            self.doc_content.clear()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при добавлении раздела: {str(e)}')

    def save_document(self):
        """Сохраняет документ."""
        if not self.doc_title.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите заголовок раздела')
            return
            
        try:
            # Определяем тип документации
            doc_type = 'admin' if self.doc_type_combo.currentText() == 'Руководство администратора' else 'user'
            
            if hasattr(self, 'current_doc_id'):
                # Обновляем существующий документ
                self.db.update_document(
                    self.current_doc_id,
                    self.doc_content.toPlainText(),
                    self.user_id,
                    self.doc_title.text()  # Передаем заголовок
                )
                # Обновляем заголовок в списке
                current_item = self.sections_list.currentItem()
                if current_item:
                    current_item.setText(self.doc_title.text())
                
                # Создаем новую версию системы
                version_id = self.create_new_version(
                    f"Обновлен раздел: {self.doc_title.text()}",
                    f"Обновлено содержание раздела документации"
                )
                
                if version_id:
                    self.db.add_version_change(
                        version_id,
                        'update',
                        'document',
                        self.current_doc_id,
                        f"Обновлен раздел '{self.doc_title.text()}'"
                    )
                
                QMessageBox.information(self, 'Успех', 'Изменения сохранены')
            else:
                # Создаем новый документ
                doc_id = self.db.add_document(
                    self.doc_title.text(),
                    self.doc_content.toPlainText(),
                    self.user_id,
                    doc_type
                )
                self.current_doc_id = doc_id
                self.sections_list.addItem(self.doc_title.text())
                
                # Создаем новую версию системы
                version_id = self.create_new_version(
                    f"Добавлен новый раздел: {self.doc_title.text()}",
                    f"Добавлен новый раздел документации типа {self.doc_type_combo.currentText()}"
                )
                
                if version_id:
                    self.db.add_version_change(
                        version_id,
                        'add',
                        'document',
                        doc_id,
                        f"Добавлен раздел '{self.doc_title.text()}'"
                    )
                
                QMessageBox.information(self, 'Успех', 'Документ создан')
            
            # Обновляем список документов
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при сохранении: {str(e)}')

    def export_document(self):
        if not self.doc_content.toPlainText():
            QMessageBox.warning(self, 'Ошибка', 'Нет содержимого для экспорта')
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            'Экспорт документации',
            '',
            'PDF (*.pdf);;HTML (*.html);;Markdown (*.md)'
        )
        
        if not file_name:
            return
            
        try:
            title = self.doc_title.text()
            content = self.doc_content.toPlainText()
            
            if file_name.endswith('.pdf'):
                export_to_pdf(file_name, title, content)
            elif file_name.endswith('.html'):
                export_to_html(file_name, title, content)
            elif file_name.endswith('.md'):
                export_to_markdown(file_name, title, content)
                
            QMessageBox.information(self, 'Успех', 'Документ успешно экспортирован')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при экспорте: {str(e)}')

    def add_glossary_term(self):
        if not self.term_input.text() or not self.definition_input.toPlainText():
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
            
        try:
            term_id = self.db.add_glossary_term(
                self.term_input.text(),
                self.definition_input.toPlainText(),
                self.user_id
            )
            self.glossary_list.addItem(f"{self.term_input.text()}: {self.definition_input.toPlainText()}")
            
            # Создаем новую версию системы
            version_id = self.create_new_version(
                f"Добавлен новый термин: {self.term_input.text()}",
                f"Добавлен новый термин в глоссарий"
            )
            
            if version_id:
                self.db.add_version_change(
                    version_id,
                    'add',
                    'glossary',
                    term_id,
                    f"Добавлен термин '{self.term_input.text()}'"
                )
            
            QMessageBox.information(self, 'Успех', 'Термин добавлен в глоссарий')
            self.term_input.clear()
            self.definition_input.clear()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при добавлении термина: {str(e)}')

    def add_faq(self):
        """Добавляет новый вопрос-ответ в FAQ."""
        if not self.question_input.text() or not self.answer_input.toPlainText():
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
            
        try:
            # Проверяем, есть ли уже такой вопрос
            faqs = self.db.get_all_faq()
            for faq in faqs:
                if faq[1] == self.question_input.text():
                    QMessageBox.warning(self, 'Ошибка', 'Такой вопрос уже существует')
                    return
            
            # Добавляем новый FAQ
            faq_id = self.db.add_faq(
                self.question_input.text(),
                self.answer_input.toPlainText(),
                self.user_id
            )
            
            # Добавляем в список
            item = QListWidgetItem(f"Q: {self.question_input.text()}\nA: {self.answer_input.toPlainText()}")
            item.setData(Qt.ItemDataRole.UserRole, faq_id)
            self.faq_list.addItem(item)
            
            # Создаем новую версию системы
            version_id = self.create_new_version(
                f"Добавлен новый FAQ: {self.question_input.text()}",
                f"Добавлен новый вопрос-ответ в FAQ"
            )
            
            if version_id:
                self.db.add_version_change(
                    version_id,
                    'add',
                    'faq',
                    faq_id,
                    f"Добавлен FAQ '{self.question_input.text()}'"
                )
            
            QMessageBox.information(self, 'Успех', 'Вопрос добавлен в FAQ')
            self.question_input.clear()
            self.answer_input.clear()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при добавлении вопроса: {str(e)}')

    def logout(self):
        """Выход из системы."""
        if self.main_window:
            self.close()
            self.main_window.logout()

    def delete_section(self):
        current_item = self.sections_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите раздел для удаления')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этот раздел?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Находим ID документа
                documents = self.db.get_all_documents()
                doc_id = None
                for doc in documents:
                    if doc[1] == current_item.text():  # doc[1] - title
                        doc_id = doc[0]
                        break
                
                if doc_id:
                    self.db.delete_document(doc_id)
                    self.sections_list.takeItem(self.sections_list.row(current_item))
                    self.doc_title.clear()
                    self.doc_content.clear()
                    QMessageBox.information(self, 'Успех', 'Раздел успешно удален')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении раздела: {str(e)}')

    def delete_glossary_term(self):
        """Удаляет выбранный термин глоссария."""
        current_item = self.glossary_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите термин для удаления')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этот термин?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Находим ID термина
                terms = self.db.get_all_glossary_terms()
                term_id = None
                term_name = None
                for term in terms:
                    if f"{term[1]}: {term[2]}" == current_item.text():  # term[1] - term name, term[2] - definition
                        term_id = term[0]
                        term_name = term[1]
                        break
                
                if term_id:
                    # Сохраняем индекс элемента перед удалением
                    row = self.glossary_list.row(current_item)
                    
                    # Удаляем термин из базы данных
                    self.db.delete_glossary_term(term_id)
                    
                    # Создаем новую версию системы
                    version_id = self.create_new_version(
                        f"Удален термин: {term_name}",
                        f"Удален термин из глоссария"
                    )
                    
                    if version_id:
                        self.db.add_version_change(
                            version_id,
                            'delete',
                            'glossary',
                            term_id,
                            f"Удален термин '{term_name}'"
                        )
                    
                    # Удаляем элемент из списка
                    self.glossary_list.takeItem(row)
                    QMessageBox.information(self, 'Успех', 'Термин успешно удален')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении термина: {str(e)}')

    def delete_faq(self):
        """Удаляет выбранный FAQ."""
        current_item = self.faq_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите вопрос для удаления')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этот вопрос?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Получаем ID FAQ из пользовательских данных элемента
                faq_id = current_item.data(Qt.ItemDataRole.UserRole)
                row = self.faq_list.row(current_item)
                
                if faq_id is not None:
                    # Получаем текст вопроса для записи в историю версий
                    faq = self.db.get_faq(faq_id)
                    faq_question = faq[1] if faq else "Неизвестный вопрос"
                    
                    # Удаляем FAQ из базы данных
                    self.db.delete_faq(faq_id)
                    
                    # Создаем новую версию системы
                    version_id = self.create_new_version(
                        f"Удален FAQ: {faq_question}",
                        f"Удален вопрос-ответ из FAQ"
                    )
                    
                    if version_id:
                        self.db.add_version_change(
                            version_id,
                            'delete',
                            'faq',
                            faq_id,
                            f"Удален FAQ '{faq_question}'"
                        )
                    
                    # Удаляем элемент из списка
                    self.faq_list.takeItem(row)
                    QMessageBox.information(self, 'Успех', 'Вопрос успешно удален')
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось получить ID вопроса')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении вопроса: {str(e)}')

    def delete_user_question(self):
        """Удаляет выбранный вопрос пользователя."""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите вопрос для удаления')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этот вопрос?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Получаем текст элемента и удаляем статус из начала строки
                item_text = current_item.text()
                if '[Отвечен]' in item_text:
                    item_text = item_text.replace('[Отвечен]', '').strip()
                elif '[Новый]' in item_text:
                    item_text = item_text.replace('[Новый]', '').strip()
                
                # Находим ID вопроса
                questions = self.db.get_user_questions_with_answers()  # Используем метод с ответами
                question_id = None
                
                for q in questions:
                    # Проверяем совпадение текста вопроса
                    if f"От {q[5]}: {q[2]}" == item_text:  # q[5] - username, q[2] - question
                        question_id = q[0]
                        break
                
                if question_id:
                    # Сохраняем индекс элемента перед удалением
                    row = self.questions_list.row(current_item)
                    
                    # Удаляем вопрос из базы данных
                    self.db.delete_user_question(question_id)
                    
                    # Удаляем элемент из списка
                    self.questions_list.takeItem(row)
                    QMessageBox.information(self, 'Успех', 'Вопрос успешно удален')
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось найти вопрос в базе данных')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении вопроса: {str(e)}')

    def load_document(self, item):
        """Загружает выбранный документ для редактирования."""
        try:
            documents = self.db.get_all_documents()
            for doc in documents:
                if doc[1] == item.text():  # doc[1] - title
                    self.current_doc_id = doc[0]
                    self.doc_title.setText(doc[1])
                    self.doc_content.setPlainText(doc[2])  # doc[2] - content
                    
                    # Загружаем версии документа
                    doc_versions = self.db.get_document_versions(self.current_doc_id)
                    self.doc_versions_list.clear()
                    for version in doc_versions:
                        item = QListWidgetItem(f"Версия {version[3]} ({version[6]}) - {version[4]}")  # version[3] - version, version[6] - username, version[4] - date
                        item.setData(Qt.ItemDataRole.UserRole, version[0])  # version[0] - id
                        self.doc_versions_list.addItem(item)
                    
                    # Загружаем оценки документа
                    self.load_document_ratings(self.current_doc_id)
                    
                    break
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке документа: {str(e)}')

    def load_document_ratings(self, doc_id):
        """Загружает оценки для выбранного документа."""
        try:
            ratings = self.db.get_document_ratings(doc_id)
            self.ratings_list.clear()
            
            if not ratings:
                self.ratings_list.addItem("Нет оценок")
                return
                
            for rating in ratings:
                # rating[2] - user_id, rating[3] - rating, rating[4] - comment, rating[6] - username
                comment = f" - {rating[4]}" if rating[4] else ""
                self.ratings_list.addItem(f"{rating[6]}: {rating[3]}/5{comment}")
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке оценок: {str(e)}')

    def create_glossary_tab(self):
        """Создает вкладку глоссария с поиском."""
        glossary_tab = QWidget()
        layout = QVBoxLayout()
        
        # Добавляем поиск
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText('Поиск по глоссарию...')
        search_input.textChanged.connect(self.filter_glossary)
        search_layout.addWidget(search_input)
        
        # Список терминов
        self.glossary_list = QListWidget()
        self.glossary_list.itemClicked.connect(self.show_glossary_term)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        add_term_btn = QPushButton('Добавить термин')
        add_term_btn.clicked.connect(self.add_glossary_term)
        edit_term_btn = QPushButton('Редактировать')
        edit_term_btn.clicked.connect(self.edit_glossary_term)
        delete_term_btn = QPushButton('Удалить термин')
        delete_term_btn.setStyleSheet('background-color: #ff6b6b; color: white;')
        delete_term_btn.clicked.connect(self.delete_glossary_term)
        buttons_layout.addWidget(add_term_btn)
        buttons_layout.addWidget(edit_term_btn)
        buttons_layout.addWidget(delete_term_btn)
        
        # Поля ввода
        self.term_input = QLineEdit()
        self.term_input.setPlaceholderText('Термин')
        self.definition_input = QTextEdit()
        self.definition_input.setPlaceholderText('Определение')
        
        layout.addLayout(search_layout)
        layout.addWidget(self.glossary_list)
        layout.addWidget(self.term_input)
        layout.addWidget(self.definition_input)
        layout.addLayout(buttons_layout)
        
        glossary_tab.setLayout(layout)
        return glossary_tab

    def filter_glossary(self, text):
        """Фильтрует термины в глоссарии."""
        for i in range(self.glossary_list.count()):
            item = self.glossary_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def insert_image(self):
        """Открывает диалог выбора изображения и вставляет его в документ."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_name:
            # Копируем изображение в папку с ресурсами
            new_path = os.path.join('resources', 'images', os.path.basename(file_name))
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.copy2(file_name, new_path)
            
            # Вставляем ссылку на изображение в формате Markdown
            cursor = self.doc_content.textCursor()
            cursor.insertText(f'![{os.path.basename(file_name)}]({new_path})')

    def add_user(self):
        """Открывает диалог добавления пользователя."""
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            is_admin = dialog.admin_checkbox.isChecked()
            
            try:
                self.db.add_user(username, password, is_admin)
                self.load_users()
                QMessageBox.information(self, 'Успех', 'Пользователь успешно добавлен')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при добавлении пользователя: {str(e)}')

    def delete_user(self):
        """Удаляет выбранного пользователя."""
        current_item = self.users_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пользователя для удаления')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этого пользователя?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                user_id = current_item.data(Qt.ItemDataRole.UserRole)
                self.db.delete_user(user_id)
                self.load_users()
                QMessageBox.information(self, 'Успех', 'Пользователь успешно удален')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении пользователя: {str(e)}')

    def load_users(self):
        """Загружает список пользователей."""
        try:
            users = self.db.get_all_users()
            self.users_list.clear()
            for user in users:
                # Проверяем, является ли пользователь админом
                is_admin = bool(user[3])  # Преобразуем в булево значение
                item = QListWidgetItem(f"{user[1]} ({'Админ' if is_admin else 'Пользователь'})")
                item.setData(Qt.ItemDataRole.UserRole, user[0])  # Сохраняем ID пользователя
                self.users_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке пользователей: {str(e)}')

    def show_version_details(self, item):
        """Показывает детали выбранной версии."""
        try:
            version_id = item.data(Qt.ItemDataRole.UserRole)
            versions = self.db.get_all_versions()
            changes = self.db.get_version_changes(version_id)
            
            for version in versions:
                if version[0] == version_id:
                    details = f"Версия: {version[1]}\n"
                    details += f"Описание: {version[2]}\n"
                    details += f"Дата создания: {version[4]}\n"
                    details += f"Автор: {version[6]}\n\n"
                    details += "Изменения:\n"
                    
                    for change in changes:
                        details += f"- {change[5]}\n"  # change[5] - description
                    
                    self.version_details.setPlainText(details)
                    break
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке деталей версии: {str(e)}')

    def show_question_details(self, item):
        """Показывает детали выбранного вопроса."""
        try:
            questions = self.db.get_user_questions_with_answers()
            
            # Получаем текст элемента и удаляем статус из начала строки
            item_text = item.text()
            if '[Отвечен]' in item_text:
                item_text = item_text.replace('[Отвечен]', '').strip()
            elif '[Новый]' in item_text:
                item_text = item_text.replace('[Новый]', '').strip()
                
            for q in questions:
                if f"От {q[5]}: {q[2]}" == item_text:  # q[5] - username, q[2] - question
                    # Если есть ответ, показываем его
                    if q[6]:  # q[6] - answer
                        self.question_answer_input.setPlainText(q[6])
                    else:
                        self.question_answer_input.clear()
                    break
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке деталей вопроса: {str(e)}')

    def answer_question(self):
        """Отвечает на выбранный вопрос."""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите вопрос для ответа')
            return
            
        if not self.question_answer_input.toPlainText():
            QMessageBox.warning(self, 'Ошибка', 'Введите ответ на вопрос')
            return
            
        try:
            # Находим ID вопроса
            questions = self.db.get_user_questions()
            question_id = None
            question_text = None
            
            # Получаем текст элемента и удаляем статус из начала строки
            item_text = current_item.text()
            if '[Отвечен]' in item_text:
                item_text = item_text.replace('[Отвечен]', '').strip()
            elif '[Новый]' in item_text:
                item_text = item_text.replace('[Новый]', '').strip()
                
            for q in questions:
                if f"От {q[5]}: {q[2]}" == item_text:  # q[5] - username, q[2] - question
                    question_id = q[0]
                    question_text = q[2]
                    break
            
            if question_id:
                # Сохраняем ответ
                if self.db.answer_user_question(
                    question_id,
                    self.question_answer_input.toPlainText(),
                    self.user_id
                ):
                    # Создаем новую версию системы
                    version_id = self.create_new_version(
                        f"Ответ на вопрос пользователя",
                        f"Добавлен ответ на вопрос пользователя и создан новый FAQ"
                    )
                    
                    if version_id:
                        self.db.add_version_change(
                            version_id,
                            'add',
                            'faq',
                            question_id,  # Используем ID вопроса как связанный ID
                            f"Ответ на вопрос '{question_text}'"
                        )
                    
                    QMessageBox.information(self, 'Успех', 'Ответ сохранен и добавлен в FAQ')
                    self.load_data()  # Обновляем списки
                    self.question_answer_input.clear()
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось сохранить ответ')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось найти вопрос в базе данных')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при сохранении ответа: {str(e)}')

    def create_new_version(self, description, changes):
        """Создает новую версию системы."""
        try:
            # Получаем последнюю версию
            latest = self.db.get_latest_version()
            if latest:
                current_version = latest[1]  # version_number
                # Увеличиваем номер версии
                version_parts = current_version.split('.')
                if len(version_parts) > 1:
                    version_parts[-1] = str(int(version_parts[-1]) + 1)
                else:
                    version_parts.append('1')
                new_version = '.'.join(version_parts)
            else:
                new_version = '1.0'
            
            # Создаем новую версию
            version_id = self.db.create_new_version(
                new_version,
                description,
                changes,
                self.user_id
            )
            
            # Обновляем список версий
            self.load_data()
            
            return version_id
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при создании версии: {str(e)}')
            return None

    def view_doc_version(self):
        """Просматривает выбранную версию документа."""
        current_item = self.doc_versions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите версию для просмотра')
            return
            
        try:
            version_id = current_item.data(Qt.ItemDataRole.UserRole)
            version = self.db.get_document_version(version_id)
            if version:
                # Создаем диалог для просмотра
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Просмотр версии {version[3]}")
                dialog.setMinimumSize(800, 600)
                
                layout = QVBoxLayout()
                content = QTextEdit()
                content.setPlainText(version[2])  # version[2] - content
                content.setReadOnly(True)
                
                buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
                buttons.rejected.connect(dialog.reject)
                
                layout.addWidget(content)
                layout.addWidget(buttons)
                dialog.setLayout(layout)
                
                dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при просмотре версии: {str(e)}')

    def restore_doc_version(self, item=None):
        """Восстанавливает выбранную версию документа."""
        if not item:
            item = self.doc_versions_list.currentItem()
            
        if not item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите версию для восстановления')
            return
            
        try:
            version_id = item.data(Qt.ItemDataRole.UserRole)
            version = self.db.get_document_version(version_id)
            if version:
                reply = QMessageBox.question(
                    self, 'Подтверждение',
                    'Вы уверены, что хотите восстановить эту версию?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.doc_content.setPlainText(version[2])  # version[2] - content
                    self.save_document()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при восстановлении версии: {str(e)}')

    def delete_doc_version(self):
        """Удаляет выбранную версию документа."""
        current_item = self.doc_versions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите версию для удаления')
            return
            
        # Проверяем, не последняя ли это версия
        if self.doc_versions_list.count() <= 1:
            QMessageBox.warning(self, 'Ошибка', 'Нельзя удалить единственную версию документа')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить эту версию?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                version_id = current_item.data(Qt.ItemDataRole.UserRole)
                # Удаляем версию из базы данных
                self.db.delete_document_version(version_id)
                # Удаляем из списка
                self.doc_versions_list.takeItem(self.doc_versions_list.row(current_item))
                QMessageBox.information(self, 'Успех', 'Версия документа удалена')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении версии: {str(e)}')

    def delete_system_version(self):
        """Удаляет выбранную версию системы."""
        current_item = self.versions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите версию для удаления')
            return
            
        # Проверяем, не последняя ли это версия
        if self.versions_list.count() <= 1:
            QMessageBox.warning(self, 'Ошибка', 'Нельзя удалить единственную версию системы')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить эту версию?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                version_id = current_item.data(Qt.ItemDataRole.UserRole)
                # Удаляем версию из базы данных
                self.db.delete_version(version_id)
                # Удаляем из списка
                self.versions_list.takeItem(self.versions_list.row(current_item))
                # Очищаем детали версии
                self.version_details.clear()
                QMessageBox.information(self, 'Успех', 'Версия системы удалена')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при удалении версии: {str(e)}')

    def show_glossary_term(self, item):
        """Показывает выбранный термин для редактирования."""
        try:
            terms = self.db.get_all_glossary_terms()
            for term in terms:
                if f"{term[1]}: {term[2]}" == item.text():  # term[1] - term name, term[2] - definition
                    self.current_term_id = term[0]
                    self.term_input.setText(term[1])
                    self.definition_input.setPlainText(term[2])
                    break
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке термина: {str(e)}')

    def edit_glossary_term(self):
        """Редактирует выбранный термин глоссария."""
        if not hasattr(self, 'current_term_id'):
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите термин для редактирования')
            return
            
        if not self.term_input.text() or not self.definition_input.toPlainText():
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
            
        try:
            self.db.update_glossary_term(
                self.current_term_id,
                self.term_input.text(),
                self.definition_input.toPlainText()
            )
            
            # Создаем новую версию системы
            version_id = self.create_new_version(
                f"Обновлен термин: {self.term_input.text()}",
                f"Обновлено определение термина в глоссарии"
            )
            
            if version_id:
                self.db.add_version_change(
                    version_id,
                    'update',
                    'glossary',
                    self.current_term_id,
                    f"Обновлен термин '{self.term_input.text()}'"
                )
            
            QMessageBox.information(self, 'Успех', 'Термин обновлен')
            self.load_data()
            self.term_input.clear()
            self.definition_input.clear()
            delattr(self, 'current_term_id')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при обновлении термина: {str(e)}')

    def show_faq(self, item):
        """Показывает выбранный FAQ для редактирования."""
        try:
            faq_id = item.data(Qt.ItemDataRole.UserRole)
            faq = self.db.get_faq(faq_id)
            if faq:
                self.current_faq_id = faq[0]
                self.question_input.setText(faq[1])
                self.answer_input.setPlainText(faq[2])
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке FAQ: {str(e)}')

    def edit_faq(self):
        """Редактирует выбранный FAQ."""
        if not hasattr(self, 'current_faq_id'):
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите вопрос для редактирования')
            return
            
        if not self.question_input.text() or not self.answer_input.toPlainText():
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
            
        try:
            self.db.update_faq(
                self.current_faq_id,
                self.question_input.text(),
                self.answer_input.toPlainText()
            )
            
            # Создаем новую версию системы
            version_id = self.create_new_version(
                f"Обновлен FAQ: {self.question_input.text()}",
                f"Обновлен вопрос-ответ в FAQ"
            )
            
            if version_id:
                self.db.add_version_change(
                    version_id,
                    'update',
                    'faq',
                    self.current_faq_id,
                    f"Обновлен FAQ '{self.question_input.text()}'"
                )
            
            QMessageBox.information(self, 'Успех', 'FAQ обновлен')
            self.load_data()
            self.question_input.clear()
            self.answer_input.clear()
            delattr(self, 'current_faq_id')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при обновлении FAQ: {str(e)}')

    def restore_system_version(self):
        """Восстанавливает систему до выбранной версии."""
        current_item = self.versions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите версию для восстановления')
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите восстановить систему до этой версии? Это может привести к потере данных.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                version_id = current_item.data(Qt.ItemDataRole.UserRole)
                if version_id is None:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось получить ID версии')
                    return
                    
                # Получаем информацию о версии
                versions = self.db.get_all_versions()
                version_info = None
                for v in versions:
                    if v[0] == version_id:
                        version_info = v
                        break
                        
                if not version_info:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось найти информацию о версии')
                    return
                
                # Восстанавливаем систему до выбранной версии
                if self.db.restore_system_to_version(version_id):
                    # Создаем новую версию системы для записи о восстановлении
                    version_number = version_info[1]  # Получаем номер версии
                    
                    new_version_id = self.create_new_version(
                        f"Восстановление до версии {version_number}",
                        f"Система восстановлена до версии {version_number}"
                    )
                    
                    if new_version_id:
                        self.db.add_version_change(
                            new_version_id,
                            'restore',
                            'system',
                            version_id,
                            f"Восстановление системы до версии {version_number}"
                        )
                    
                    # Обновляем данные
                    self.load_data()
                    
                    QMessageBox.information(self, 'Успех', f'Система успешно восстановлена до версии {version_number}')
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось восстановить систему до выбранной версии')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при восстановлении системы: {str(e)}')

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить пользователя')
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Поле для имени пользователя
        username_layout = QHBoxLayout()
        username_label = QLabel('Имя пользователя:')
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Поле для пароля
        password_layout = QHBoxLayout()
        password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # Чекбокс для роли администратора
        self.admin_checkbox = QCheckBox('Администратор')
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addWidget(self.admin_checkbox)
        layout.addWidget(buttons)
        
        self.setLayout(layout) 