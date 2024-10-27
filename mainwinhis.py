import sys
import sqlite3
from datetime import datetime, timedelta
import csv
import json
import random
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QDateEdit,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QFileDialog,
    QDialog,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QComboBox,
    QProgressBar,
    QFrame,
    QStackedWidget,
)
from PyQt6.QtGui import (
    QColor,
    QIcon,
    QFont,
    QPalette,
    QLinearGradient,
    QBrush,
    QPainter,
)
from PyQt6.QtCore import Qt, QSize, QDate, QTimer, QPropertyAnimation, QEasingCurve, QTime

[... Las clases anteriores se mantienen igual hasta SalesHistoryWidget ...]

class SalesHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.page = 1
        self.items_per_page = 20
        self.total_items = 0
        self.current_sort = "fecha"
        self.sort_order = "DESC"
        self.init_ui()
        self.setup_database()  # Añadimos inicialización de la base de datos
        self.load_sales_history()  # Cargamos los datos inicialmente

    def setup_database(self):
        """Configura la base de datos y añade datos de ejemplo si está vacía"""
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()

        # Crear las tablas si no existen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                producto_id INTEGER,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                precio REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        """)

        # Verificar si hay datos
        cursor.execute("SELECT COUNT(*) FROM ventas")
        if cursor.fetchone()[0] == 0:
            # Añadir datos de ejemplo
            # Clientes de ejemplo
            clientes = ["Juan Pérez", "María García", "Carlos López", "Ana Martínez", "Pedro Rodríguez"]
            for cliente in clientes:
                cursor.execute("INSERT INTO clientes (nombre) VALUES (?)", (cliente,))

            # Productos de ejemplo
            productos = [
                ("Laptop", 999.99),
                ("Smartphone", 599.99),
                ("Tablet", 299.99),
                ("Auriculares", 79.99),
                ("Monitor", 249.99)
            ]
            for producto in productos:
                cursor.execute("INSERT INTO productos (nombre, precio) VALUES (?, ?)", producto)

            # Generar ventas de ejemplo
            for _ in range(50):  # 50 ventas de ejemplo
                cliente_id = random.randint(1, len(clientes))
                fecha = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
                total = 0
                
                # Insertar venta
                cursor.execute(
                    "INSERT INTO ventas (cliente_id, fecha, total) VALUES (?, ?, ?)",
                    (cliente_id, fecha, total)
                )
                venta_id = cursor.lastrowid

                # Generar detalles de venta
                num_productos = random.randint(1, 3)
                venta_total = 0
                for _ in range(num_productos):
                    producto_id = random.randint(1, len(productos))
                    cantidad = random.randint(1, 3)
                    precio_unitario = productos[producto_id-1][1]
                    precio = cantidad * precio_unitario
                    venta_total += precio

                    cursor.execute("""
                        INSERT INTO detalles_venta 
                        (venta_id, producto_id, cantidad, precio_unitario, precio)
                        VALUES (?, ?, ?, ?, ?)
                    """, (venta_id, producto_id, cantidad, precio_unitario, precio))

                # Actualizar el total de la venta
                cursor.execute(
                    "UPDATE ventas SET total = ? WHERE id = ?",
                    (venta_total, venta_id)
                )

        conn.commit()
        conn.close()

    def init_ui(self):
        [... Código del init_ui anterior ...]

        # Mejoras en la tabla
        self.sales_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e6ed;
                border: none;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e0e6ed;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1a237e;
            }
            QHeaderView::section {
                background-color: #f5f7fa;
                color: #2c3e50;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e0e6ed;
            }
        """)
        
        # Añadir widget para espacio vacío
        empty_widget = QWidget()
        empty_widget.setStyleSheet("""
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #f5f7fa,
                stop:1 #e4e7eb
            );
            border-radius: 8px;
            margin: 10px;
        """)
        empty_layout = QVBoxLayout(empty_widget)
        
        # Mensaje cuando no hay datos
        self.empty_message = QLabel("No hay ventas registradas")
        self.empty_message.setStyleSheet("""
            color: #7f8c8d;
            font-size: 16px;
            font-weight: bold;
        """)
        self.empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.empty_message)
        
        # Stacked Widget para alternar entre tabla y mensaje vacío
        self.stack = QStackedWidget()
        self.stack.addWidget(self.sales_table)
        self.stack.addWidget(empty_widget)
        
        # Reemplazar la tabla en el layout con el stacked widget
        content_layout = self.layout()
        content_layout.addWidget(self.stack)

    def load_sales_history(self):
        """Carga el historial de ventas desde la base de datos"""
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()

        # Obtener el conteo total
        cursor.execute("SELECT COUNT(*) FROM ventas")
        self.total_items = cursor.fetchone()[0]

        if self.total_items == 0:
            self.stack.setCurrentIndex(1)  # Mostrar mensaje vacío
            return

        self.stack.setCurrentIndex(0)  # Mostrar tabla
        # Obtener los datos paginados
        offset = (self.page - 1) * self.items_per_page
        query = f"""
            SELECT v.id, c.nombre, v.fecha, v.total
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY {self.current_sort} {self.sort_order}
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (self.items_per_page, offset))
        sales_data = cursor.fetchall()
        conn.close()

        # Llenar la tabla
        self.populate_table(sales_data)
        self.update_pagination()

    def populate_table(self, sales):
        """Llena la tabla con los datos de ventas"""
        self.sales_table.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            # Formatear los datos
            sale_id = str(sale[0])
            client_name = sale[1]
            date = datetime.strptime(sale[2], "%Y-%m-%d").strftime("%d/%m/%Y")
            total = f"${sale[3]:.2f}"

            # Crear los items de la tabla
            items = [sale_id, client_name, date, total]
            for col, value in enumerate(items):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.sales_table.setItem(row, col, item)

            # Botón de detalles
            view_button = ModernButton("Ver Detalles", "#3498db")
            view_button.clicked.connect(lambda _, s=sale[0]: self.show_sale_details(s))
            self.sales_table.setCellWidget(row, 4, view_button)

    def show_sale_details(self, sale_id):
        details_dialog = SaleDetailsDialog(sale_id, self)
        details_dialog.exec()

[... El resto de las clases se mantienen igual ...]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aplicar estilo global
    app.setStyle("Fusion")
    
    # Crear y mostrar la ventana principal
    window = QMainWindow()
    window.setWindowTitle("Sistema de Gestión de Ventas")
    window.setMinimumSize(1200, 800)
    
    # Establecer el widget central
    central_widget = SalesHistoryWidget()
    window.setCentralWidget(central_widget)
    
    window.show()
    sys.exit(app.exec())