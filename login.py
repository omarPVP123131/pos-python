from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QFrame,
    QGraphicsOpacityEffect,  # Importación añadida
)
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
    QTimer,
    QParallelAnimationGroup,
    QPoint,  # Importación añadida
    pyqtSignal
)
from PyQt6.QtGui import QColor, QIcon, QPainter, QLinearGradient
import sqlite3


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
        self.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                padding: 15px 20px;
                background-color: rgba(255, 255, 255, 0.8);
                color: #333;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """
        )


class ModernButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;

            }
            QPushButton:pressed {
                background-color: #2573a7;

            }
        """
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)


class LoginModule(QWidget):
    login_success = pyqtSignal(int)  # Añade esto
    show_register_form = pyqtSignal()  # Nueva señal para mostrar el formulario de registro
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left side - Gradient background with logo
        left_widget = GradientWidget(QColor("#3498db"), QColor("#2c3e50"))
        left_widget.setFixedWidth(400)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label = QLabel()
        logo_label.setPixmap(QIcon("path_to_your_logo.png").pixmap(QSize(150, 150)))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(logo_label)

        company_name = QLabel("Your Company Name")
        company_name.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        company_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(company_name)

        main_layout.addWidget(left_widget)

        # Right side - Login form
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(50, 50, 50, 50)

        welcome_label = QLabel("Welcome back!")
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(welcome_label)

        self.username_input = ModernLineEdit("Username")
        right_layout.addWidget(self.username_input)

        self.password_input = ModernLineEdit("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        right_layout.addWidget(self.password_input)

        self.login_button = ModernButton("Log In")
        self.login_button.clicked.connect(self.attempt_login)
        right_layout.addWidget(self.login_button)

        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: #e74c3c; font-size: 16px;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.message_label)

        # Agregar separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        right_layout.addWidget(separator)

        # Agregar botón de registro
        register_layout = QHBoxLayout()
        register_label = QLabel("¿No tienes una cuenta?")
        register_label.setStyleSheet("color: #333; font-size: 14px;")
        register_layout.addWidget(register_label)

        self.register_button = QPushButton("Regístrate")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
        """)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.clicked.connect(self.show_register_form.emit)
        register_layout.addWidget(self.register_button)

        right_layout.addLayout(register_layout)

        right_layout.addStretch()

        main_layout.addWidget(right_widget)

        right_layout.addStretch()

        main_layout.addWidget(right_widget)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()
        c.execute(
            "SELECT * FROM usuarios WHERE username=? AND password=?",
            (username, password),
        )
        user = c.fetchone()
        conn.close()

        if user:
            user_id = user[0]  # Asumiendo que el id del usuario es el primer campo
            self.message_label.setText("Login successful!")
            self.message_label.setStyleSheet("color: #2ecc71; font-size: 16px;")
            self.animate_success()
            self.login_success.emit(user_id)  # Emitir la señal aquí

        else:
            self.message_label.setText("Incorrect username or password")
            self.message_label.setStyleSheet("color: #e74c3c; font-size: 16px;")
            self.animate_failure()

    def animate_success(self):
        self.animate_message()
        self.animate_button(True)

    def animate_failure(self):
        self.animate_message()
        self.animate_button(False)

    def animate_message(self):
        # Aplicar QGraphicsOpacityEffect al QLabel antes de animar
        opacity_effect = QGraphicsOpacityEffect(self.message_label)
        self.message_label.setGraphicsEffect(opacity_effect)

        animation = QPropertyAnimation(
            opacity_effect, b"opacity"
        )  # Animar la opacidad del efecto
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()

    def animate_button(self, success):
        original_style = self.login_button.styleSheet()
        if success:
            self.login_button.setStyleSheet(
                original_style + "background-color: #2ecc71;"
            )
        else:
            # Animación de sacudida
            shake_animation = QPropertyAnimation(self.login_button, b"pos")
            shake_animation.setDuration(100)
            shake_animation.setLoopCount(3)

            # Usar QPoint para la animación de la posición
            shake_animation.setKeyValueAt(0, self.login_button.pos())
            shake_animation.setKeyValueAt(0.25, self.login_button.pos() + QPoint(5, 0))
            shake_animation.setKeyValueAt(0.75, self.login_button.pos() + QPoint(-5, 0))
            shake_animation.setKeyValueAt(1, self.login_button.pos())

            # Animación de color
            color_animation = QPropertyAnimation(self.login_button, b"styleSheet")
            color_animation.setDuration(300)
            color_animation.setStartValue(original_style + "background-color: #e74c3c;")
            color_animation.setEndValue(original_style)

            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(shake_animation)
            animation_group.addAnimation(color_animation)
            animation_group.start()

        QTimer.singleShot(1000, lambda: self.login_button.setStyleSheet(original_style))
