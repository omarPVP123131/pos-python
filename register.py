from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QHBoxLayout, QFrame, QProgressBar, QSizePolicy, QCheckBox, QDialog, QTextEdit
)
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QLinearGradient, QIcon
import sqlite3
import bcrypt
from datetime import datetime
import re
import json

class GradientWidget(QWidget):
    def __init__(self, start_color, end_color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_color = start_color
        self.end_color = end_color

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.start_color)
        gradient.setColorAt(1, self.end_color)
        painter.fillRect(self.rect(), gradient)

class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                padding: 10px 15px;
                background-color: #f5f5f5;
                color: #333;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)

class ModernButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2573a7;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class PasswordStrengthBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setRange(0, 100)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                height: 5px;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                border-radius: 2px;
            }
        """)
    
    def update_strength(self, password):
        strength = 0
        if len(password) >= 8:
            strength += 25
        if re.search(r"[A-Z]", password):
            strength += 25
        if re.search(r"[a-z]", password):
            strength += 25
        if re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", password):
            strength += 25

        self.setValue(strength)
        if strength < 50:
            self.setStyleSheet("""
                QProgressBar::chunk { background-color: #e74c3c; }
            """)
        elif strength < 75:
            self.setStyleSheet("""
                QProgressBar::chunk { background-color: #f39c12; }
            """)
        else:
            self.setStyleSheet("""
                QProgressBar::chunk { background-color: #2ecc71; }
            """)

class BackArrowButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon("icons/flecha.png"))
        self.setIconSize(QSize(24, 24))
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class TermsAndConditionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Términos y Condiciones")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        with open("terms_and_conditions.json", "r", encoding="utf-8") as file:
            terms = json.load(file)
            text_edit.setPlainText(terms["content"])
        
        layout.addWidget(text_edit)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class RegisterModule(QWidget):
    registro_exitoso = pyqtSignal()
    regresar_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_widget = GradientWidget(QColor("#3498db"), QColor("#2c3e50"))
        left_widget.setFixedWidth(300)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Registro de Usuario")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)

        description = QLabel("Únete a nuestra comunidad y disfruta de todos los beneficios.")
        description.setStyleSheet("color: white; font-size: 14px;")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(description)

        main_layout.addWidget(left_widget)

        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(40, 40, 40, 40)

        back_button = BackArrowButton()
        back_button.clicked.connect(self.regresar)
        right_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.txt_username = ModernLineEdit("Nombre de usuario")
        right_layout.addWidget(self.txt_username)

        self.txt_email = ModernLineEdit("Correo electrónico")
        right_layout.addWidget(self.txt_email)

        self.txt_password = ModernLineEdit("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.textChanged.connect(self.update_password_strength)
        right_layout.addWidget(self.txt_password)

        self.password_strength_bar = PasswordStrengthBar()
        right_layout.addWidget(self.password_strength_bar)

        self.txt_confirm_password = ModernLineEdit("Confirmar contraseña")
        self.txt_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        right_layout.addWidget(self.txt_confirm_password)

        terms_layout = QHBoxLayout()
        self.terms_checkbox = QCheckBox("Acepto los")
        self.terms_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        terms_layout.addWidget(self.terms_checkbox)

        terms_button = QPushButton("términos y condiciones")
        terms_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                text-decoration: underline;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        terms_button.setCursor(Qt.CursorShape.PointingHandCursor)
        terms_button.clicked.connect(self.show_terms_and_conditions)
        terms_layout.addWidget(terms_button)
        terms_layout.addStretch()

        right_layout.addLayout(terms_layout)

        self.btn_registrar = ModernButton("Registrar")
        self.btn_registrar.clicked.connect(self.registrar_usuario)
        right_layout.addWidget(self.btn_registrar)

        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        right_layout.addWidget(self.message_label)

        main_layout.addWidget(right_widget)

    def update_password_strength(self, password):
        self.password_strength_bar.update_strength(password)

    def registrar_usuario(self):
        username = self.txt_username.text()
        password = self.txt_password.text()
        confirm_password = self.txt_confirm_password.text()
        email = self.txt_email.text()

        if not username or not password or not confirm_password or not email:
            self.show_message("Todos los campos son obligatorios.", error=True)
            return

        if password != confirm_password:
            self.show_message("Las contraseñas no coinciden.", error=True)
            return

        if not self.is_valid_email(email):
            self.show_message("El formato del correo electrónico no es válido.", error=True)
            return

        if self.password_strength_bar.value() < 75:
            self.show_message("La contraseña es demasiado débil. Por favor, elija una contraseña más fuerte.", error=True)
            return

        if not self.terms_checkbox.isChecked():
            self.show_message("Debe aceptar los términos y condiciones.", error=True)
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO usuarios (username, password, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
                      (username, hashed_password, email, 'usuario', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            self.show_message("Usuario registrado correctamente.", error=False)
            self.registro_exitoso.emit()
            self.limpiar_campos()
        except sqlite3.IntegrityError:
            self.show_message("El nombre de usuario ya existe.", error=True)
        finally:
            conn.close()

    def show_message(self, message, error=False):
        self.message_label.setText(message)
        color = "#e74c3c" if error else "#2ecc71"
        self.message_label.setStyleSheet(f"color: {color}; font-size: 14px;")
        
        animation = QPropertyAnimation(self.message_label, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()

    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def limpiar_campos(self):
        self.txt_username.clear()
        self.txt_password.clear()
        self.txt_confirm_password.clear()
        self.txt_email.clear()
        self.password_strength_bar.setValue(0)
        self.terms_checkbox.setChecked(False)

    def regresar(self):
        self.regresar_signal.emit()

    def show_terms_and_conditions(self):
        dialog = TermsAndConditionsDialog(self)
        dialog.exec()