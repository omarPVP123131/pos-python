import sys
import sqlite3
from datetime import datetime
import csv
import json
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
from PyQt6.QtCharts import (
    QChart,
    QChartView,
    QBarSet,
    QBarSeries,
    QValueAxis,
    QBarCategoryAxis,
    QPieSeries,
)


class DigitalClock(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Digital-7', 'Segoe UI', monospace;
                background: rgba(0, 0, 0, 0.2);
                padding: 8px 16px;
                border-radius: 8px;
            }
        """)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        current_time = QTime.currentTime()
        display_text = current_time.toString('hh:mm:ss AP')  # Formato de 12 horas  
        self.setText(display_text)

class ModernButton(QPushButton):
    def __init__(self, text, color, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {QColor(color).darker(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(color).darker(120).name()};
            }}
        """)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
            self.setStyleSheet(self.styleSheet() + " padding-left: 10px; padding-right: 10px;")  # Espacio para el icono


class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 8px;
                height: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:1 #2ecc71
                );
                border-radius: 8px;
            }
        """)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setDuration(1000)

    def animate_progress(self, start, end):
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

class SalesHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.page = 1
        self.items_per_page = 20
        self.total_items = 0
        self.current_sort = "fecha"
        self.sort_order = "DESC"
        self.init_ui()
        self.load_sales_history()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header con diseño moderno
        header = QWidget()
        header.setObjectName("header")
        header.setStyleSheet("""
            #header {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, 
                    stop:1 #3498db
                );
                min-height: 80px;
            }
        """)
        header_layout = QHBoxLayout(header)

        # Logo y título con diseño moderno
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        
        title_label = QLabel("Sistema de Gestión de Ventas")
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
        """)
        
        subtitle_label = QLabel("Panel de Control")
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addWidget(title_container)
        
     # Reloj Digital
        self.clock = DigitalClock()
        header_layout.addWidget(self.clock, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(header)


        # Contenido principal
        content = QWidget()
        content.setObjectName("content")
        content.setStyleSheet("""
            #content {
                background-color: #f5f7fa;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        content_layout = QVBoxLayout(content)

        # Pestañas con estilo moderno
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e6ed;
                background: white;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #f5f7fa;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 4px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border: 1px solid #e0e6ed;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: white;
                color: #3498db;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #e0e6ed;
            }
        """)

        # Pestaña de ventas mejorada
        sales_tab = self.create_sales_tab()
        tab_widget.addTab(sales_tab, "📊 Historial de Ventas")
        
        # Dashboard mejorado
        dashboard_tab = DashboardWidget()
        tab_widget.addTab(dashboard_tab, "🏠 Dashboard")

        content_layout.addWidget(tab_widget)
        main_layout.addWidget(content)

    def create_sales_tab(self):
        sales_widget = QWidget()
        sales_layout = QVBoxLayout(sales_widget)

        # Barra de herramientas mejorada
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setStyleSheet("""
            #toolbar {
                background: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)

        # Búsqueda mejorada
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_icon = QLabel("🔍")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ID o Cliente")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e6ed;
                border-radius: 5px;
                background: #f5f7fa;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background: white;
            }
        """)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_container)

        # Filtros mejorados
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #e0e6ed;
                border-radius: 5px;
                background: #f5f7fa;
            }
        """)
        toolbar_layout.addWidget(self.date_filter)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Fecha ↓", "Total ↓", "Cliente A-Z"])
        self.sort_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #e0e6ed;
                border-radius: 5px;
                background: #f5f7fa;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        toolbar_layout.addWidget(self.sort_combo)

        sales_layout.addWidget(toolbar)

        # Tabla mejorada con nuevo diseño
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(
            ["ID", "Cliente", "Fecha", "Total", "Acciones"]
        )
        
        # Estilo mejorado de la tabla
        self.sales_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e0e6ed;
                border: none;
                border-radius: 12px;
                selection-background-color: #3498db;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            
            QTableWidget::item {
                padding: 16px;
                border-bottom: 1px solid #e0e6ed;
                color: #2c3e50;
                font-size: 15px;
            }
            
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
                font-weight: 500;
            }
            
            QHeaderView::section {
                background-color: #f8fafc;
                color: #1e293b;
                font-weight: bold;
                font-size: 16px;
                padding: 20px 15px;
                border: none;
                border-bottom: 2px solid #e0e6ed;
                border-right: 1px solid #e0e6ed;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            QHeaderView::section:hover {
                background-color: #e3f2fd;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #f8fafc;
                width: 12px;
                border-radius: 6px;
                margin: 15px 0px 15px 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #94a3b8;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
            
            QScrollBar::add-line:vertical {
                height: 15px;
                background: none;
            }
            
            QScrollBar::sub-line:vertical {
                height: 15px;
                background: none;
            }
            
            QTableWidget::item:focus {
                border: none;
                outline: none;
            }
            
            QTableWidget QTableCornerButton::section {
                background-color: #f8fafc;
                border: none;
            }
        """)

        # Configuraciones adicionales de la tabla
        self.sales_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sales_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setShowGrid(False)
        self.sales_table.setAlternatingRowColors(True)
        
        # Establecer altura mínima para las filas
        self.sales_table.verticalHeader().setDefaultSectionSize(60)
        
        # Establecer el ancho de las columnas
        self.sales_table.setColumnWidth(0, 100)  # ID
        self.sales_table.setColumnWidth(1, 250)  # Cliente
        self.sales_table.setColumnWidth(2, 200)  # Fecha
        self.sales_table.setColumnWidth(3, 150)  # Total
        
        # Ajustar el espaciado interno de la tabla
        self.sales_table.setContentsMargins(20, 20, 20, 20)
        
        # Animación suave al seleccionar filas
        self.sales_table.setStyleSheet(self.sales_table.styleSheet() + """
            QTableWidget::item {
            }
        """)

        sales_layout.addWidget(self.sales_table)


        # Paginación mejorada
        pagination = QWidget()
        pagination.setObjectName("pagination")
        pagination.setStyleSheet("""
            #pagination {
                background: white;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        pagination_layout = QHBoxLayout(pagination)

        self.prev_button = QPushButton("← Anterior")
        self.next_button = QPushButton("Siguiente →")
        self.page_label = QLabel("Página 1 de 10")
        
        for button in [self.prev_button, self.next_button]:
            button.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border: 1px solid #3498db;
                    border-radius: 5px;
                    color: #3498db;
                    background: white;
                }
                QPushButton:hover {
                    background: #3498db;
                    color: white;
                }
                QPushButton:disabled {
                    border-color: #bdc3c7;
                    color: #bdc3c7;
                }
            """)

        self.page_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 14px;
            font-weight: bold;
        """)

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        sales_layout.addWidget(pagination)

         # Barra de acciones mejorada con botones de exportación
        actions = QWidget()
        actions.setObjectName("actions")
        actions.setStyleSheet("""
            #actions {
                background: white;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                border: 1px solid #e0e6ed;
            }
        """)
        actions_layout = QHBoxLayout(actions)

        export_buttons = [
            ("CSV", "📊", self.export_to_csv),
            ("JSON", "📝", self.export_to_json),
            ("XML", "📄", self.export_to_xml)
        ]

        for format, icon, func in export_buttons:
            button = QPushButton(f"{icon} Exportar {format}")
            button.setStyleSheet("""
                QPushButton {
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2ecc71,
                        stop:1 #27ae60
                    );
                }
                QPushButton:hover {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #27ae60,
                        stop:1 #219a52
                    );
                }
                QPushButton:pressed {
                    background: #219a52;
                }
            """)
            button.clicked.connect(lambda checked, f=format.lower(): self.export_data(f))
            actions_layout.addWidget(button)

        sales_layout.addWidget(actions)

        # Barra de progreso mejorada
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background: #f5f7fa;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #3498db;
                border-radius: 5px;
            }
        """)
        sales_layout.addWidget(self.progress_bar)

        return sales_widget

    def load_sales_history(self):
        """Carga el historial de ventas desde la base de datos con una barra de progreso animada."""
        # Inicializar la barra de progreso
        self.progress_bar.setValue(0)

        # Paso 1: Simular progreso inicial (0 a 50)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress_load_data)
        self.timer.start(50)  # Actualización cada 50ms

    def update_progress_load_data(self):
        """Actualiza el progreso de la barra y carga los datos."""
        current_value = self.progress_bar.value()

        if current_value < 50:
            # Progresar de 0 a 50 de forma animada
            self.progress_bar.setValue(current_value + 1)
        else:
            # Detener la animación cuando llegue a 50
            self.timer.stop()

            # Paso 2: Cargar los datos de la base de datos
            self.load_data_from_database()

            # Paso 3: Completar el progreso (50 a 100)
            self.timer = QTimer()
            self.timer.timeout.connect(self.complete_progress)
            self.timer.start(50)

    def load_data_from_database(self):
        """Carga los datos de la base de datos y los coloca en la tabla."""
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()

        # Obtener el conteo total
        cursor.execute("SELECT COUNT(*) FROM ventas")
        self.total_items = cursor.fetchone()[0]

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

        # Poner los datos en la tabla
        self.populate_table(sales_data)

        # Actualizar la paginación
        self.update_pagination()

    def complete_progress(self):
        """Completa la animación del progreso (50 a 100)."""
        current_value = self.progress_bar.value()

        if current_value < 100:
            # Incrementar de 50 a 100
            self.progress_bar.setValue(current_value + 1)
        else:
            # Detener la animación cuando llegue a 100
            self.timer.stop()

    def populate_table(self, sales):
        self.sales_table.setRowCount(len(sales))
        
        # Estilo de la tabla
        self.sales_table.setAlternatingRowColors(True)

        for row, sale in enumerate(sales):
            for col, value in enumerate(sale):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.sales_table.setItem(row, col, item)

            view_button = ModernButton("Ver", "#3498db", "icons/view.png")
            view_button.clicked.connect(lambda _, s=sale[0]: self.show_sale_details(s))
            self.sales_table.setCellWidget(row, 4, view_button)

            # Aplicar estilo al botón
            view_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)

    def filter_sales(self):
        search_text = self.search_input.text().lower()
        date_filter = self.date_filter.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()

        query = """
            SELECT v.id, c.nombre, v.fecha, v.total
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            WHERE (LOWER(v.id) LIKE ? OR LOWER(c.nombre) LIKE ?)
            AND v.fecha LIKE ?
        """
        cursor.execute(
            query, (f"%{search_text}%", f"%{search_text}%", f"%{date_filter}%")
        )
        filtered_sales = cursor.fetchall()

        conn.close()

        self.populate_table(filtered_sales)

    def change_sort(self, index):
        sort_options = ["fecha", "total", "c.nombre"]
        self.current_sort = sort_options[index]
        self.sort_order = "DESC" if self.sort_order == "ASC" else "ASC"
        self.page = 1
        self.load_sales_history()

    def update_pagination(self):
        total_pages = (self.total_items - 1) // self.items_per_page + 1
        self.page_label.setText(f"Página {self.page} de {total_pages}")
        self.prev_button.setEnabled(self.page > 1)
        self.next_button.setEnabled(self.page < total_pages)

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.load_sales_history()

    def next_page(self):
        total_pages = (self.total_items - 1) // self.items_per_page + 1
        if self.page < total_pages:
            self.page += 1
            self.load_sales_history()

    def show_sale_details(self, sale_id):
        details_dialog = SaleDetailsDialog(sale_id, self)
        details_dialog.exec()

    def export_data(self, format):
        file_formats = {
            "csv": ("CSV Files (*.csv)", "w", ""),
            "json": ("JSON Files (*.json)", "w", ""),
            "xml": ("XML Files (*.xml)", "wb", ""),
        }

        file_name, _ = QFileDialog.getSaveFileName(
            self, f"Guardar archivo {format.upper()}", "", file_formats[format][0]
        )
        if file_name:
            conn = sqlite3.connect("pos_database.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.id, c.nombre, v.fecha, v.total
                FROM ventas v
                JOIN clientes c ON v.cliente_id = c.id
                ORDER BY v.fecha DESC
            """
            )
            sales = cursor.fetchall()
            conn.close()

            if format == "csv":
                self.export_to_csv(file_name, sales)
            elif format == "json":
                self.export_to_json(file_name, sales)
            elif format == "xml":
                self.export_to_xml(file_name, sales)

            QMessageBox.information(
                self, "Éxito", f"Los datos han sido exportados a {file_name}"
            )

    def export_to_csv(self, file_name, sales):
        with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["ID Venta", "Cliente", "Fecha", "Total"])
            csv_writer.writerows(sales)

    def export_to_json(self, file_name, sales):
        data = [
            {"id": sale[0], "cliente": sale[1], "fecha": sale[2], "total": sale[3]}
            for sale in sales
        ]
        with open(file_name, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)

    def export_to_xml(self, file_name, sales):
        root = ET.Element("ventas")
        for sale in sales:
            venta = ET.SubElement(root, "venta")
            ET.SubElement(venta, "id").text = str(sale[0])
            ET.SubElement(venta, "cliente").text = sale[1]
            ET.SubElement(venta, "fecha").text = sale[2]
            ET.SubElement(venta, "total").text = str(sale[3])

        tree = ET.ElementTree(root)
        tree.write(file_name, encoding="utf-8", xml_declaration=True)


class SaleDetailsDialog(QDialog):
    def __init__(self, sale_id, parent=None):
        super().__init__(parent)
        self.sale_id = sale_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Detalles de la Venta #{self.sale_id}")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Información general de la venta
        info_layout = QHBoxLayout()
        self.sale_info_label = QLabel()
        info_layout.addWidget(self.sale_info_label)
        layout.addLayout(info_layout)

        # Tabla de productos
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(
            ["ID Producto", "Producto", "Cantidad", "Precio Unitario", "Subtotal"]
        )
        self.products_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.products_table)

        # Total

        self.total_label = QLabel()
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_label)

        # Botón de cerrar
        close_button = ModernButton("Cerrar", "#3498db")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.load_sale_details()

    def load_sale_details(self):
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()

        # Obtener información general de la venta
        cursor.execute(
            """
            SELECT v.id, c.nombre, v.fecha, v.total
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            WHERE v.id = ?
        """,
            (self.sale_id,),
        )
        sale_info = cursor.fetchone()

        if sale_info:
            self.sale_info_label.setText(
                f"Venta #{sale_info[0]} | Cliente: {sale_info[1]} | Fecha: {sale_info[2]}"
            )
            self.total_label.setText(f"Total: ${sale_info[3]:.2f}")

        # Obtener detalles de los productos
        cursor.execute(
            """
            SELECT d.producto_id, p.nombre, d.cantidad, d.precio_unitario, d.precio
            FROM detalles_venta d
            JOIN productos p ON d.producto_id = p.id
            WHERE d.venta_id = ?
        """,
            (self.sale_id,),
        )
        products = cursor.fetchall()

        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, value in enumerate(product):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.products_table.setItem(row, col, item)

        conn.close()


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Resumen de ventas
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(
            self.create_summary_card(
                "Ventas Totales", self.get_total_sales(), "#3498db"
            )
        )
        summary_layout.addWidget(
            self.create_summary_card(
                "Ventas del Mes", self.get_monthly_sales(), "#2ecc71"
            )
        )
        summary_layout.addWidget(
            self.create_summary_card(
                "Clientes Totales", self.get_total_customers(), "#e74c3c"
            )
        )
        layout.addLayout(summary_layout)

        # Gráficos
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.create_sales_chart())
        charts_layout.addWidget(self.create_products_chart())
        layout.addLayout(charts_layout)

    def create_summary_card(self, title, value, color):
        card = QWidget()
        card.setStyleSheet(
            f"""
            background-color: {color};
            border-radius: 10px;
            padding: 20px;
        """
        )
        card_layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 16px;")
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        return card

    def get_total_sales(self):
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM ventas")
        total = cursor.fetchone()[0]
        conn.close()
        return f"${total:.2f}" if total else "$0.00"

    def get_monthly_sales(self):
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()
        current_month = datetime.now().strftime("%Y-%m")
        cursor.execute(
            "SELECT SUM(total) FROM ventas WHERE fecha LIKE ?", (f"{current_month}%",)
        )
        total = cursor.fetchone()[0]
        conn.close()
        return f"${total:.2f}" if total else "$0.00"

    def get_total_customers(self):
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT cliente_id) FROM ventas")
        count = cursor.fetchone()[0]
        conn.close()
        return str(count)

    def create_sales_chart(self):
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT strftime('%Y-%m', v.fecha) as month, SUM(d.cantidad * d.precio_unitario) as total
            FROM detalles_venta d
            JOIN ventas v ON d.venta_id = v.id
            GROUP BY month
            ORDER BY month
            LIMIT 6
        """
        )
        data = cursor.fetchall()
        conn.close()

        # Crear el gráfico
        chart = QChart()
        series = QBarSeries()

        bar_set = QBarSet("Ventas Mensuales")
        for _, value in data:
            bar_set.append(value)
        series.append(bar_set)

        chart.addSeries(series)
        chart.setTitle("Ventas por Mes")

        # Configurar el eje X
        axis_x = QBarCategoryAxis()
        axis_x.append([month for month, _ in data])
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # Configurar el eje Y
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Configurar la vista del gráfico
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view

    def create_products_chart(self):
        conn = sqlite3.connect("pos_database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.nombre, SUM(d.cantidad) as total_vendido
            FROM detalles_venta d
            JOIN productos p ON d.producto_id = p.id
            GROUP BY d.producto_id
            ORDER BY total_vendido DESC
            LIMIT 5
        """
        )
        data = cursor.fetchall()
        conn.close()

        chart = QChart()
        series = QPieSeries()

        for name, value in data:
            slice = series.append(name, value)
            slice.setLabelVisible()

        chart.addSeries(series)
        chart.setTitle("Productos más Vendidos")

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesHistoryWidget()
    window.show()
    sys.exit(app.exec())
