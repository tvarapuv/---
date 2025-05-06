from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QTextBrowser, QPushButton, QListWidget,
                           QTabWidget, QLineEdit, QMessageBox, QSpinBox,
                           QFileDialog, QComboBox, QGroupBox, QTextEdit)
from PyQt6.QtCore import Qt
import markdown
from utils import export_to_pdf, export_to_html, export_to_markdown

class UserWindow(QMainWindow):
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
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Поиск...')
        self.search_input.textChanged.connect(self.filter_documents)  # Добавляем фильтрацию при вводе
        search_btn = QPushButton('Найти')
        search_btn.clicked.connect(self.search_documents)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        # Фильтр по типу документации
        filter_layout = QHBoxLayout()
        filter_label = QLabel('Тип документации:')
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['Все', 'Руководство пользователя', 'Руководство администратора'])
        self.filter_combo.currentIndexChanged.connect(self.filter_documents)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        
        sections_label = QLabel('Разделы документации')
        self.sections_list = QListWidget()
        self.sections_list.itemClicked.connect(self.load_document)
        
        # Добавляем кнопку выхода
        logout_btn = QPushButton('Выйти из системы')
        logout_btn.setStyleSheet('background-color: #ff6b6b; color: white; padding: 5px;')
        logout_btn.clicked.connect(self.logout)
        
        left_layout.addLayout(search_layout)
        left_layout.addLayout(filter_layout)
        left_layout.addWidget(sections_label)
        left_layout.addWidget(self.sections_list)
        left_layout.addStretch()
        left_layout.addWidget(logout_btn)  # Добавляем кнопку выхода внизу
        left_panel.setLayout(left_layout)
        
        # Правая панель с табами
        right_panel = QTabWidget()
        
        # Таб просмотра документации
        doc_tab = QWidget()
        doc_layout = QVBoxLayout()
        
        self.doc_title = QLabel()
        self.doc_content = QTextBrowser()
        self.doc_content.setOpenExternalLinks(True)
        
        # Панель оценки
        rating_layout = QHBoxLayout()
        rating_label = QLabel('Оценка:')
        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(1, 5)
        self.rating_comment = QLineEdit()
        self.rating_comment.setPlaceholderText('Комментарий к оценке')
        rate_btn = QPushButton('Оценить')
        rate_btn.clicked.connect(self.rate_document)
        
        rating_layout.addWidget(rating_label)
        rating_layout.addWidget(self.rating_spin)
        rating_layout.addWidget(self.rating_comment)
        rating_layout.addWidget(rate_btn)
        
        # Кнопка экспорта
        export_btn = QPushButton('Экспортировать')
        export_btn.clicked.connect(self.export_document)
        
        doc_layout.addWidget(self.doc_title)
        doc_layout.addWidget(self.doc_content)
        doc_layout.addLayout(rating_layout)
        doc_layout.addWidget(export_btn)
        doc_tab.setLayout(doc_layout)
        
        # Таб глоссария
        glossary_tab = QWidget()
        glossary_layout = QVBoxLayout()
        
        # Поиск в глоссарии
        glossary_search_layout = QHBoxLayout()
        self.glossary_search_input = QLineEdit()
        self.glossary_search_input.setPlaceholderText('Поиск в глоссарии...')
        self.glossary_search_input.textChanged.connect(self.filter_glossary)
        glossary_search_layout.addWidget(self.glossary_search_input)
        
        self.glossary_list = QListWidget()
        
        glossary_layout.addLayout(glossary_search_layout)
        glossary_layout.addWidget(self.glossary_list)
        glossary_tab.setLayout(glossary_layout)
        
        # Таб FAQ
        faq_tab = QWidget()
        faq_layout = QVBoxLayout()
        
        # Поиск в FAQ
        faq_search_layout = QHBoxLayout()
        self.faq_search_input = QLineEdit()
        self.faq_search_input.setPlaceholderText('Поиск в FAQ...')
        self.faq_search_input.textChanged.connect(self.filter_faq)
        faq_search_layout.addWidget(self.faq_search_input)
        
        self.faq_list = QListWidget()
        
        faq_layout.addLayout(faq_search_layout)
        faq_layout.addWidget(self.faq_list)
        faq_tab.setLayout(faq_layout)
        
        # Таб вопросов
        questions_tab = QWidget()
        questions_layout = QVBoxLayout()
        
        # Список моих вопросов
        my_questions_group = QGroupBox('Мои вопросы')
        my_questions_layout = QVBoxLayout()
        self.questions_list = QListWidget()
        
        # Поле для нового вопроса
        new_question_group = QGroupBox('Задать вопрос')
        new_question_layout = QVBoxLayout()
        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText('Введите ваш вопрос...')
        
        ask_btn = QPushButton('Отправить вопрос')
        ask_btn.clicked.connect(self.ask_question)
        
        new_question_layout.addWidget(self.question_input)
        new_question_layout.addWidget(ask_btn)
        new_question_group.setLayout(new_question_layout)
        
        my_questions_layout.addWidget(self.questions_list)
        my_questions_group.setLayout(my_questions_layout)
        
        questions_layout.addWidget(my_questions_group)
        questions_layout.addWidget(new_question_group)
        questions_tab.setLayout(questions_layout)
        
        # Добавляем табы
        right_panel.addTab(doc_tab, "Документация")
        right_panel.addTab(glossary_tab, "Глоссарий")
        right_panel.addTab(faq_tab, "FAQ")
        right_panel.addTab(questions_tab, "Вопросы")
        
        # Добавляем панели в главный layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.setWindowTitle('Система документации')
        self.setGeometry(100, 100, 1200, 800)
        
        # Загружаем данные
        self.load_data()
        self.current_doc_id = None

    def load_data(self):
        # Загружаем документы
        self.all_documents = self.db.get_all_documents()
        self.sections_list.clear()
        for doc in self.all_documents:
            self.sections_list.addItem(doc[1])  # doc[1] - title
            
        # Загружаем термины глоссария
        self.all_terms = self.db.get_all_glossary_terms()
        self.glossary_list.clear()
        for term in self.all_terms:
            self.glossary_list.addItem(f"{term[1]}: {term[2]}")  # term[1] - term name, term[2] - definition
        
        # Загружаем FAQ
        self.all_faqs = self.db.get_all_faq()
        self.faq_list.clear()
        for faq in self.all_faqs:
            self.faq_list.addItem(f"Q: {faq[1]}\nA: {faq[2]}")  # faq[1] - question, faq[2] - answer
        
        # Загружаем вопросы пользователя с ответами
        questions = self.db.get_user_questions_with_answers(self.user_id)
        self.questions_list.clear()
        for q in questions:
            status = '[Отвечен]' if q[3] == 'answered' else '[Ожидает ответа]'
            question_text = f"{status} Вопрос: {q[2]}"
            if q[3] == 'answered' and q[6]:  # Если вопрос отвечен и есть ответ
                question_text += f"\nОтвет: {q[6]}"
            self.questions_list.addItem(question_text)

    def filter_documents(self):
        """Фильтрует документы по типу и поисковому запросу."""
        search_text = self.search_input.text().lower()
        filter_type = self.filter_combo.currentText()
        
        self.sections_list.clear()
        
        for doc in self.all_documents:
            # Фильтрация по типу
            doc_type = 'Руководство администратора' if doc[7] == 'admin' else 'Руководство пользователя'
            if filter_type != 'Все' and doc_type != filter_type:
                continue
                
            # Фильтрация по поисковому запросу
            if search_text and search_text not in doc[1].lower() and search_text not in doc[2].lower():
                continue
                
            # Добавляем документ, если он прошел фильтрацию
            self.sections_list.addItem(doc[1])  # doc[1] - title

    def search_documents(self):
        """Выполняет поиск документов по запросу."""
        query = self.search_input.text()
        if not query:
            self.load_data()
            return
            
        try:
            documents = self.db.search_documents(query)
            self.all_documents = documents  # Обновляем список всех документов
            self.filter_documents()  # Применяем фильтрацию
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при поиске: {str(e)}')

    def load_document(self, item):
        try:
            documents = self.db.get_all_documents()
            for doc in documents:
                if doc[1] == item.text():  # doc[1] - title
                    self.current_doc_id = doc[0]
                    self.doc_title.setText(doc[1])
                    self.doc_content.setMarkdown(doc[2])  # doc[2] - content
                    break
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке документа: {str(e)}')

    def rate_document(self):
        if not self.current_doc_id:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите документ')
            return
            
        try:
            self.db.add_rating(
                self.current_doc_id,
                self.user_id,
                self.rating_spin.value(),
                self.rating_comment.text()
            )
            QMessageBox.information(self, 'Успех', 'Спасибо за вашу оценку!')
            self.rating_comment.clear()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при сохранении оценки: {str(e)}')

    def ask_question(self):
        """Отправляет новый вопрос."""
        if not self.question_input.toPlainText():
            QMessageBox.warning(self, 'Ошибка', 'Введите ваш вопрос')
            return
            
        try:
            self.db.add_user_question(
                self.user_id,
                self.question_input.toPlainText()
            )
            QMessageBox.information(self, 'Успех', 'Ваш вопрос отправлен')
            self.question_input.clear()
            self.load_data()  # Обновляем список вопросов
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при отправке вопроса: {str(e)}')

    def export_document(self):
        if not self.current_doc_id:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите документ')
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
            content = self.doc_content.toPlainText()
            title = self.doc_title.text()
            
            if file_name.endswith('.pdf'):
                export_to_pdf(file_name, title, content)
            elif file_name.endswith('.html'):
                export_to_html(file_name, title, content)
            elif file_name.endswith('.md'):
                export_to_markdown(file_name, title, content)
                
            QMessageBox.information(self, 'Успех', 'Документ успешно экспортирован')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при экспорте: {str(e)}')

    def logout(self):
        """Выход из системы."""
        if self.main_window:
            self.close()
            self.main_window.logout()

    def filter_glossary(self):
        """Фильтрует термины глоссария по поисковому запросу."""
        search_text = self.glossary_search_input.text().lower()
        
        self.glossary_list.clear()
        
        for term in self.all_terms:
            # Если поисковый запрос пустой или найден в термине или определении
            if not search_text or search_text in term[1].lower() or search_text in term[2].lower():
                self.glossary_list.addItem(f"{term[1]}: {term[2]}")  # term[1] - term name, term[2] - definition 

    def filter_faq(self):
        """Фильтрует FAQ по поисковому запросу."""
        search_text = self.faq_search_input.text().lower()
        
        self.faq_list.clear()
        
        for faq in self.all_faqs:
            # Если поисковый запрос пустой или найден в вопросе или ответе
            if not search_text or search_text in faq[1].lower() or search_text in faq[2].lower():
                self.faq_list.addItem(f"Q: {faq[1]}\nA: {faq[2]}")  # faq[1] - question, faq[2] - answer 