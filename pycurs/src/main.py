import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from database import Database
from admin_window import AdminWindow
from user_window import UserWindow

#Окно входа в систему
class LoginWindow(QWidget):
    def __init__(self, db): #Получение объекта базы данных дб
        super().__init__() #Конструктор родительского класса
        self.db = db
        self.admin_window = None 
        self.user_window = None
        self.init_ui() #Вызов для создания

    def init_ui(self): #Создание интерфейса окна
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel('Система документации')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Поле логина
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Имя пользователя')
        layout.addWidget(self.username_input)
        
        # Поле пароля
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('Пароль')
        layout.addWidget(self.password_input)
        
        # Выбор роли
        self.role_combo = QComboBox()
        self.role_combo.addItems(['Пользователь', 'Администратор'])
        layout.addWidget(self.role_combo)
        
        # Кнопки и подключение к обработчикам
        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        register_btn = QPushButton('Зарегистрироваться')
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)
        
        self.setLayout(layout)
        self.setWindowTitle('Вход в систему')
        self.setGeometry(300, 300, 300, 200)

    def login(self): #Получение логина и пароля из полей ввода, если есть соответсвующие окна
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя пользователя и пароль')
            return
            
        user = self.db.get_user(username, password) #Проверка пользователей в базе
        if user:
            user_id = user[0]  # ID пользователя
            is_admin = bool(user[3])  # Проверяем, является ли пользователь админом
            
            self.hide()
            if is_admin:
                self.show_admin_window(user_id)
            else:
                self.show_user_window(user_id)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверное имя пользователя или пароль')

    def register(self): #Получение логина и пароля проверка 
        username = self.username_input.text()
        password = self.password_input.text()
        is_admin = self.role_combo.currentText() == 'Администратор'
        
        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя пользователя и пароль')
            return
            
        # Проверяем, существует ли пользователь
        user = self.db.get_user(username, password)
        if user:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь с таким именем уже существует')
            return
            
        try:
            # Регистрируем нового пользователя с выбранной ролью
            user_id = self.db.add_user(username, password, is_admin)
            
            if is_admin:
                # Добавляем примеры данных для администратора
                self.db.add_example_data(user_id)
                
            QMessageBox.information(self, 'Успех', 'Регистрация успешна')
            
            # Автоматически входим в систему
            self.hide()
            if is_admin:
                self.show_admin_window(user_id)
            else:
                self.show_user_window(user_id)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка при регистрации: {str(e)}')
#Окрытие окна администратора
    def show_admin_window(self, user_id):
        if self.admin_window:
            self.admin_window.close()
            
        self.admin_window = AdminWindow(self.db, user_id, self)
        self.admin_window.show()
 #Окно пользователя    
    def show_user_window(self, user_id):
        if self.user_window:
            self.user_window.close()
            
        self.user_window = UserWindow(self.db, user_id, self)
        self.user_window.show()
        
    def logout(self):
        # Закрываем окна пользователя или администратора
        if self.admin_window:
            self.admin_window.close()
            self.admin_window = None
            
        if self.user_window:
            self.user_window.close()
            self.user_window = None
            
        # Очищаем поля ввода
        self.username_input.clear()
        self.password_input.clear()
        
        # Показываем окно входа
        self.show()
        
        QMessageBox.information(self, 'Выход', 'Вы успешно вышли из системы')

def check_admin_exists(db):
    """Проверяет, существует ли администратор, и создает его при необходимости."""
    users = db.get_all_users()
    admin_exists = False
    
    for user in users:
        if user[3]:  # user[3] - is_admin
            admin_exists = True
            break
            
    if not admin_exists:
        # Создаем администратора по умолчанию
        try:
            admin_id = db.add_user('admin', 'admin', True)
            # Добавляем примеры данных
            db.add_example_data(admin_id)
            QMessageBox.information(
                None, 
                'Информация', 
                'Создан администратор по умолчанию:\nЛогин: admin\nПароль: admin\n\nРекомендуется сменить пароль после первого входа.'
            )
        except Exception as e:
            QMessageBox.warning(None, 'Ошибка', f'Ошибка при создании администратора: {str(e)}')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        self.check_admin_exists()
        # Показываем окно входа
        self.login_window.show()
        
    def check_admin_exists(self):
        """Проверяет, существует ли администратор, и создает его при необходимости."""
        users = self.db.get_all_users()
        admin_exists = False
        
        for user in users:
            if user[3]:  # user[3] - is_admin
                admin_exists = True
                break
                
        if not admin_exists:
            # Создаем администратора по умолчанию
            try:
                admin_id = self.db.add_user('admin', 'admin', True)
                # Добавляем примеры данных
                self.db.add_example_data(admin_id)
                QMessageBox.information(
                    self, 
                    'Информация', 
                    'Создан администратор по умолчанию:\nЛогин: admin\nПароль: admin\n\nРекомендуется сменить пароль после первого входа.'
                )
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при создании администратора: {str(e)}')
#ПЗапуск системы и октрытие соответсвующих окон
    def init_ui(self):
        self.setWindowTitle('Система документации')
        self.setGeometry(100, 100, 1200, 800)
        self.hide()

    def show_admin_window(self, user_id):
        self.login_window.hide()  # Скрываем окно входа
        
        if not hasattr(self, 'admin_window'):
            self.admin_window = AdminWindow(self.db, user_id, self)
        else:
            self.admin_window.close()
            self.admin_window = AdminWindow(self.db, user_id, self)
            
        self.admin_window.show()

    def show_user_window(self, user_id):
        self.login_window.hide()  # Скрываем окно входа
        
        if not hasattr(self, 'user_window'):
            self.user_window = UserWindow(self.db, user_id, self)
        else:
            self.user_window.close()
            self.user_window = UserWindow(self.db, user_id, self)
            
        self.user_window.show()

    def logout(self):
        # Закрываем окна пользователя или администратора
        if hasattr(self, 'admin_window'):
            self.admin_window.close()
            
        if hasattr(self, 'user_window'):
            self.user_window.close()
            
        # Очищаем поля ввода
        self.login_window.username_input.clear()
        self.login_window.password_input.clear()
        
        # Показываем окно входа
        self.show_login_window()
        
        QMessageBox.information(self, 'Выход', 'Вы успешно вышли из системы')

    def show_login_window(self):
        """Показывает окно входа."""
        # Скрываем главное окно
        self.hide()
        # Показываем окно входа как отдельное окно
        self.login_window.show()
#Запуск системы
if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = Database()
    check_admin_exists(db)
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec()) 