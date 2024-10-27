import sys
import types
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QGraphicsOpacityEffect,
    QMessageBox,
    QPushButton,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QFontDatabase, QFont
import sqlite3

# Modules
from login import LoginModule
from pos import POSModule
from inventory import InventoryModule
from customers import CustomersModule
from suppliers import SuppliersModule
from estadisticas import StatisticsModule
from Historial import SalesHistoryWidget
from calculator import CalculatorModule
from settings import SettingsModule
from local_server import LocalServerModule
from dashboard import DashboardModule
from myprofile import ProfileModule
from register import RegisterModule


class AnimatedButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, text, icon_path):
        super().__init__()
        self.setFixedHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.is_checked = False

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(24, 24)))
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("color: #333; font-size: 16px;")

        layout = QHBoxLayout(self)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.setContentsMargins(10, 0, 10, 0)

        self.setStyleSheet(
            """
            AnimatedButton {
                border: none;
                border-radius: 5px;
                background-color: transparent;
            }
            AnimatedButton:hover {
                background-color: #e0e0e0;
            }
        """
        )

    def setChecked(self, checked):
        self.is_checked = checked
        if checked:
            self.setStyleSheet(
                """
                AnimatedButton {
                    background-color: #3498db;
                    border-radius: 5px;
                }
                QLabel {
                    color: white;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                AnimatedButton {
                    background-color: transparent;
                    border-radius: 5px;
                }
                AnimatedButton:hover {
                    background-color: #e0e0e0;
                }
                QLabel {
                    color: #333;
                }
            """
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern POS System")
        self.setGeometry(100, 100, 1200, 800)
        self.is_logged_in = False
        self.animating = False
        self.user_id = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #f5f5f5;")
        sidebar_layout = QVBoxLayout(self.sidebar)

        main_layout.addWidget(self.sidebar)
        self.sidebar.setVisible(False)

        modules = [
            ("Dashboard", "dashboard_icon.png", DashboardModule),
            ("Punto De Venta", "pos_icon.png", POSModule),
            ("Inventario", "inventory_icon.png", InventoryModule),
            ("Clientes", "customers_icon.png", CustomersModule),
            ("Proveedores", "suppliers_icon.png", SuppliersModule),
            ("Reportes", "statistics_icon.png", StatisticsModule),
            ("Historial", "Historial.png", SalesHistoryWidget),
            ("Calculadora", "calculator_icon.png", CalculatorModule),
            ("Configuracion", "settings_icon.png", SettingsModule),
            ("Mi Perfil", "profile_icon.png", ProfileModule),
        ]


        self.sidebar_buttons = []

        def connect_button(button, module):
            button.clicked.connect(lambda: self.on_sidebar_button_clicked(module))

        for text, icon, module in modules:
            button = AnimatedButton(text, icon)
            sidebar_layout.addWidget(button)
            self.sidebar_buttons.append(button)
            connect_button(button, module)

        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area, 1)

        self.modules = {}
        for _, _, module in modules:
            if module != ProfileModule:
                self.modules[module] = module()
                self.content_area.addWidget(self.modules[module])

        self.login_module = LoginModule()
        self.login_module.login_success.connect(self.on_login_success)
        self.login_module.show_register_form.connect(self.show_register_form)
        self.content_area.addWidget(self.login_module)

        self.register_module = RegisterModule()
        self.register_module.registro_exitoso.connect(self.on_register_success)
        self.register_module.regresar_signal.connect(self.show_login_form)
        self.content_area.addWidget(self.register_module)

        self.content_area.setCurrentWidget(self.login_module)

    def show_register_form(self):
        self.content_area.setCurrentWidget(self.register_module)

    def show_login_form(self):
        self.content_area.setCurrentWidget(self.login_module)

    def on_register_success(self):
        QMessageBox.information(
            self,
            "Registro exitoso",
            "Usuario registrado correctamente. Por favor, inicie sesión.",
        )
        self.show_login_form()


    def on_sidebar_button_clicked(self, module):
        if not self.is_logged_in or self.animating:
            return

        sender = self.sender()
        for button in self.sidebar_buttons:
            button.setChecked(button == sender)

        if module == ProfileModule:
            if not hasattr(self, "profile_module"):
                self.profile_module = ProfileModule(self.user_id)
                self.content_area.addWidget(self.profile_module)
            widget = self.profile_module
        else:
            # Inicializar el módulo solo cuando se necesite
            if isinstance(self.modules[module], types.LambdaType):
                self.modules[module] = self.modules[module]()
                self.content_area.addWidget(self.modules[module])
            widget = self.modules[module]


        if self.content_area.currentWidget() == widget:
            QMessageBox.information(
                self, "Info", f"Ya estás en el módulo de {module.__name__}."
            )
            return

        self.animating = True
        for button in self.sidebar_buttons:
            button.setEnabled(False)

        current_widget = self.content_area.currentWidget()
        opacity_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(opacity_effect)

        self.fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.fade_anim.start()

        self.fade_anim.finished.connect(
            lambda: self.on_animation_finished(widget, opacity_effect)
        )

    def on_animation_finished(self, widget, opacity_effect):
        self.content_area.setCurrentWidget(widget)
        opacity_effect.setOpacity(1)

        for button in self.sidebar_buttons:
            button.setEnabled(True)

        self.animating = False

    def on_login_success(self, user_id):
        self.is_logged_in = True
        self.user_id = user_id
        self.sidebar.setVisible(True)
        self.content_area.setCurrentWidget(self.modules[DashboardModule])

    def on_logout(self):
        self.is_logged_in = False
        self.user_id = None
        self.sidebar.setVisible(False)
        if hasattr(self, "profile_module"):
            self.content_area.removeWidget(self.profile_module)
            del self.profile_module
        self.content_area.setCurrentWidget(self.login_module)


def create_database():
    conn = sqlite3.connect("pos_database.db")
    c = conn.cursor()

    c.execute(
        """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        role TEXT,
        email TEXT,
        login_time TEXT,
        logout_time TEXT,
        profile_picture TEXT,
        created_at TEXT
    )
    """
    )

    c.execute(
        """
    CREATE TABLE IF NOT EXISTS user_notes (
        user_id INTEGER PRIMARY KEY,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES usuarios (id)
    )
    """
    )

    c.execute(
        """
    CREATE TABLE IF NOT EXISTS user_goals (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        goal TEXT,
        target_date TEXT,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES usuarios (id)
    )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            cliente_id INTEGER,  -- Nueva columna para referenciar a clientes
            fecha TEXT,
            total REAL,
            FOREIGN KEY (user_id) REFERENCES usuarios (id),
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
        """
    )


    c.execute(
        """CREATE TABLE IF NOT EXISTS productos
                 (id INTEGER PRIMARY KEY,
                 nombre TEXT, 
                 precio REAL, 
                 stock INTEGER, 
                 proveedor_id INTEGER, 
                 imagen TEXT,
                 FOREIGN KEY (proveedor_id) REFERENCES proveedores(id))"""
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS detalles_venta (
            id INTEGER PRIMARY KEY,
            venta_id INTEGER,
            producto_id INTEGER,
            cantidad REAL,
            precio REAL,
            precio_unitario REAL,
            FOREIGN KEY (venta_id) REFERENCES ventas (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
        """
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS roles
                 (id INTEGER PRIMARY KEY, nombre TEXT)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS permisos
                 (id INTEGER PRIMARY KEY, nombre TEXT)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS roles_permisos
                 (id INTEGER PRIMARY KEY, role_id INTEGER, permiso_id INTEGER,
                 FOREIGN KEY (role_id) REFERENCES roles(id),
                 FOREIGN KEY (permiso_id) REFERENCES permisos(id))"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS proveedores
                 (id INTEGER PRIMARY KEY, nombre TEXT, contacto TEXT, telefono TEXT, email TEXT)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS metodos_pago
                 (id INTEGER PRIMARY KEY, nombre TEXT)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS cortes_caja
                 (id INTEGER PRIMARY KEY, fecha TEXT, monto_inicial REAL, monto_final REAL)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS arqueos
                 (id INTEGER PRIMARY KEY, fecha TEXT, monto_sistema REAL, monto_fisico REAL, 
                 diferencia REAL)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS promociones
                 (id INTEGER PRIMARY KEY, nombre TEXT, descripcion TEXT, 
                 fecha_inicio TEXT, fecha_fin TEXT, descuento REAL)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS clientes
                 (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT, telefono TEXT)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS puntos
                 (id INTEGER PRIMARY KEY, cliente_id INTEGER, cantidad INTEGER,
                 FOREIGN KEY (cliente_id) REFERENCES clientes(id))"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS estadisticas
                 (id INTEGER PRIMARY KEY, fecha TEXT, tipo TEXT, valor REAL)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS notas
                 (id INTEGER PRIMARY KEY, titulo TEXT, contenido TEXT, fecha TEXT)"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS respaldo_automatico
                 (id INTEGER PRIMARY KEY, fecha TEXT, ruta TEXT)"""
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
