from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QGroupBox,
    QPushButton, QFrame, QSpacerItem, QSizePolicy, QTableWidgetItem,
    QHeaderView, QComboBox, QDateEdit, QLineEdit, QProgressBar,
    QScrollArea, QTabWidget, QCalendarWidget, QDialog, QFormLayout, QGridLayout, QMessageBox,
    QApplication
)
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import os
import webbrowser
import sqlite3
from datetime import datetime, timedelta
import random

class DashboardModule(QWidget):
    refresh_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
        self.refresh_signal.connect(self.load_data)
        
        # Configurar un temporizador para actualizar los datos cada 5 minutos
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.load_data)
        self.update_timer.start(300000)  # 300000 ms = 5 minutos

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Estilo general mejorado
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333;
                font-family: Arial, sans-serif;
            }
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 1em;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                gridline-color: #d0d0d0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: 1px solid #2980b9;
                font-weight: bold;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        # Título del Dashboard con animación
        self.title_label = QLabel("Dashboard de Ventas")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title_label.setStyleSheet("""
            color: #2c3e50;
            margin: 10px 0;
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9);
            border-radius: 10px;
            padding: 10px;
            color: white;
        """)
        main_layout.addWidget(self.title_label)

        # Tabs para organizar el contenido
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #333;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.tab_widget.addTab(self.create_overview_tab(), "Resumen")
        self.tab_widget.addTab(self.create_sales_tab(), "Ventas")
        self.tab_widget.addTab(self.create_products_tab(), "Productos")
        self.tab_widget.addTab(self.create_customers_tab(), "Clientes")
        self.tab_widget.addTab(self.create_inventory_tab(), "Inventario")
        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

    def create_overview_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Resumen de Ventas
        layout.addWidget(self.create_sales_summary())

        # Gráficos
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.create_sales_chart())
        charts_layout.addWidget(self.create_product_categories_chart())
        layout.addLayout(charts_layout)

        # KPIs
        layout.addWidget(self.create_kpi_widget())

        tab.setLayout(layout)
        return tab

    def create_sales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Filtros de ventas
        filters_group = QGroupBox("Filtros de Ventas")
        filters_layout = QHBoxLayout()
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_to = QDateEdit(QDate.currentDate())
        filters_layout.addWidget(QLabel("Desde:"))
        filters_layout.addWidget(self.date_from)
        filters_layout.addWidget(QLabel("Hasta:"))
        filters_layout.addWidget(self.date_to)
        self.apply_filters_button = QPushButton("Aplicar Filtros")
        self.apply_filters_button.clicked.connect(self.apply_sales_filters)
        filters_layout.addWidget(self.apply_filters_button)
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        # Tabla de ventas
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Total", "Estado"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sales_table)

        tab.setLayout(layout)
        return tab

    def create_products_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Top productos
        layout.addWidget(self.create_top_products_table())

        # Gráfico de stock de productos
        layout.addWidget(self.create_product_stock_chart())

        tab.setLayout(layout)
        return tab

    def create_customers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Top clientes
        layout.addWidget(self.create_top_customers_table())

        # Gráfico de retención de clientes
        layout.addWidget(self.create_customer_retention_chart())

        tab.setLayout(layout)
        return tab

    def create_inventory_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Tabla de inventario
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels(["Producto", "Stock Actual", "Stock Mínimo", "Estado"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.inventory_table)

        # Botón para actualizar inventario
        update_inventory_button = QPushButton("Actualizar Inventario")
        update_inventory_button.clicked.connect(self.show_update_inventory_dialog)
        layout.addWidget(update_inventory_button)

        tab.setLayout(layout)
        return tab

    def create_sales_summary(self):
        group_box = QGroupBox("Resumen de Ventas")
        layout = QHBoxLayout()

        # Total de Ventas
        self.total_sales_label = QLabel("Total de Ventas: $0")
        self.total_sales_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.total_sales_label)

        # Ventas de Hoy
        self.today_sales_label = QLabel("Ventas de Hoy: $0")
        self.today_sales_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.today_sales_label)

        # Número de Transacciones
        self.transactions_label = QLabel("Transacciones: 0")
        self.transactions_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.transactions_label)

        group_box.setLayout(layout)
        return group_box

    def create_sales_chart(self):
        group_box = QGroupBox("Gráfico de Ventas Mensuales")
        layout = QVBoxLayout()

        self.sales_chart_widget = QLabel("Cargando gráfico...")
        layout.addWidget(self.sales_chart_widget)

        group_box.setLayout(layout)
        return group_box

    def create_product_categories_chart(self):
        group_box = QGroupBox("Ventas por Categoría de Producto")
        layout = QVBoxLayout()

        self.categories_chart_widget = QLabel("Cargando gráfico...")
        layout.addWidget(self.categories_chart_widget)

        group_box.setLayout(layout)
        return group_box

    def create_kpi_widget(self):
        group_box = QGroupBox("KPIs")
        group_box.setObjectName("KPIs")  # Añadir un nombre de objeto para facilitar la búsqueda
        layout = QGridLayout()

        kpis = [
            ("Ticket Promedio", "$0"),
            ("Margen de Beneficio", "0%"),
            ("Tasa de Conversión", "0%"),
            ("Productos por Venta", "0")
        ]

        for i, (kpi_name, kpi_value) in enumerate(kpis):
            name_label = QLabel(kpi_name)
            value_label = QLabel(kpi_value)
            value_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            layout.addWidget(name_label, i // 2, (i % 2) * 2)
            layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)

        group_box.setLayout(layout)
        return group_box

    def create_top_products_table(self):
        group_box = QGroupBox("Productos Más Vendidos")
        layout = QVBoxLayout()

        self.top_products_table = QTableWidget(5, 3)
        self.top_products_table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Total Ventas"])
        self.top_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.top_products_table)

        group_box.setLayout(layout)
        return group_box

    def create_product_stock_chart(self):
        group_box = QGroupBox("Stock de Productos")
        layout = QVBoxLayout()

        self.stock_chart_widget = QLabel("Cargando gráfico...")
        layout.addWidget(self.stock_chart_widget)

        group_box.setLayout(layout)
        return group_box

    def create_top_customers_table(self):
        group_box = QGroupBox("Clientes Principales")
        layout = QVBoxLayout()

        self.top_customers_table = QTableWidget(5, 3)
        self.top_customers_table.setHorizontalHeaderLabels(["Cliente", "Total Compras", "Última Compra"])
        self.top_customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.top_customers_table)

        group_box.setLayout(layout)
        return group_box

    def create_customer_retention_chart(self):
        group_box = QGroupBox("Retención de Clientes")
        layout = QVBoxLayout()

        self.retention_chart_widget = QLabel("Cargando gráfico...")
        layout.addWidget(self.retention_chart_widget)

        group_box.setLayout(layout)
        return group_box

    def load_data(self):
        # Simulación de carga de datos (reemplazar con conexión real a la base de datos)
        self.load_sales_summary()
        self.load_sales_chart()
        self.load_product_categories_chart()
        self.load_kpis()
        self.load_top_products()
        self.load_product_stock_chart()
        self.load_top_customers()
        self.load_customer_retention_chart()
        self.load_inventory()
        self.load_sales_table()

    def load_sales_summary(self):
        # Simulación de datos
        total_sales = random.uniform(10000, 50000)
        today_sales = random.uniform(1000, 5000)
        transactions = random.randint(50, 200)

        self.total_sales_label.setText(f"Total de Ventas: ${total_sales:.2f}")
        self.today_sales_label.setText(f"Ventas de Hoy: ${today_sales:.2f}")
        self.transactions_label.setText(f"Transacciones: {transactions}")

    def load_sales_chart(self):
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        sales = [random.randint(5000, 15000) for _ in range(6)]

        fig = go.Figure(data=[go.Bar(x=months, y=sales)])
        fig.update_layout(title='Ventas Mensuales', xaxis_title='Mes', yaxis_title='Ventas ($)')
        
        # Guardar el gráfico como HTML y mostrarlo en el QLabel
        plot(fig, filename='sales_chart.html', auto_open=False)
        self.sales_chart_widget.setText('<img src="sales_chart.html" width="100%" height="300">')

    def load_product_categories_chart(self):
        categories = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Libros']
        sales = [random.randint(1000, 5000) for _ in range(5)]

        fig = go.Figure(data=[go.Pie(labels=categories, values=sales)])
        fig.update_layout(title='Ventas por Categoría')
        
        plot(fig, filename='categories_chart.html', auto_open=False)
        self.categories_chart_widget.setText('<img src="categories_chart.html" width="100%" height="300">')

    def load_kpis(self):
        avg_ticket = random.uniform(50, 200)
        profit_margin = random.uniform(0.1, 0.4)
        conversion_rate = random.uniform(0.01, 0.1)
        products_per_sale = random.uniform(1.5, 4)

        kpi_group_box = self.findChild(QGroupBox, "KPIs")
        if kpi_group_box:
            kpi_layout = kpi_group_box.layout()
            if kpi_layout:
                kpi_layout.itemAtPosition(0, 1).widget().setText(f"${avg_ticket:.2f}")
                kpi_layout.itemAtPosition(0, 3).widget().setText(f"{profit_margin:.1%}")
                kpi_layout.itemAtPosition(1, 1).widget().setText(f"{conversion_rate:.1%}")
                kpi_layout.itemAtPosition(1, 3).widget().setText(f"{products_per_sale:.1f}")
            else:
                print("Error: No se pudo encontrar el layout de KPIs")
        else:
            print("Error: No se pudo encontrar el QGroupBox de KPIs")

    def load_top_products(self):
        products = [
            ("Smartphone XYZ", random.randint(50, 200), random.uniform(5000, 20000)),
            ("Laptop ABC", random.randint(30, 100), random.uniform(3000, 15000)),
            ("Auriculares Inalámbricos", random.randint(100, 300), random.uniform(2000, 10000)),
            ("Smartwatch 123", random.randint(40, 150), random.uniform(1500, 8000)),
            ("Tablet UVW", random.randint(20, 80), random.uniform(1000, 6000))
        ]

        for row, (product, quantity, total) in enumerate(products):
            self.top_products_table.setItem(row, 0, QTableWidgetItem(product))
            self.top_products_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.top_products_table.setItem(row, 2, QTableWidgetItem(f"${total:.2f}"))

    def load_product_stock_chart(self):
        products = ['Prod A', 'Prod B', 'Prod C', 'Prod D', 'Prod E']
        stock = [random.randint(10, 100) for _ in range(5)]

        fig = go.Figure(data=[go.Bar(x=products, y=stock)])
        fig.update_layout(title='Stock de Productos', xaxis_title='Producto', yaxis_title='Unidades en Stock')
        
        plot(fig, filename='stock_chart.html', auto_open=False)
        self.stock_chart_widget.setText('<img src="stock_chart.html" width="100%" height="300">')

    def load_top_customers(self):
        customers = [
            ("Juan Pérez", random.uniform(1000, 5000), "2023-05-15"),
            ("María García", random.uniform(800, 4000), "2023-05-18"),
            ("Carlos Rodríguez", random.uniform(600, 3000), "2023-05-20"),
            ("Ana Martínez", random.uniform(500, 2500), "2023-05-22"),
            ("Luis Sánchez", random.uniform(400, 2000), "2023-05-25")
        ]

        for row, (customer, total, last_purchase) in enumerate(customers):
            self.top_customers_table.setItem(row, 0, QTableWidgetItem(customer))
            self.top_customers_table.setItem(row, 1, QTableWidgetItem(f"${total:.2f}"))
            self.top_customers_table.setItem(row, 2, QTableWidgetItem(last_purchase))

    def load_customer_retention_chart(self):
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        new_customers = [random.randint(20, 50) for _ in range(6)]
        returning_customers = [random.randint(30, 80) for _ in range(6)]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=new_customers, name='Nuevos Clientes'))
        fig.add_trace(go.Bar(x=months, y=returning_customers, name='Clientes Recurrentes'))
        fig.update_layout(title='Retención de Clientes', xaxis_title='Mes', yaxis_title='Número de Clientes', barmode='group')
        
        plot(fig, filename='retention_chart.html', auto_open=False)
        self.retention_chart_widget.setText('<img src="retention_chart.html" width="100%" height="300">')

    def load_inventory(self):
        products = [
            ("Smartphone XYZ", random.randint(10, 50), 20),
            ("Laptop ABC", random.randint(5, 30), 15),
            ("Auriculares Inalámbricos", random.randint(20, 100), 50),
            ("Smartwatch 123", random.randint(15, 60), 30),
            ("Tablet UVW", random.randint(10, 40), 25)
        ]

        self.inventory_table.setRowCount(len(products))
        for row, (product, current_stock, min_stock) in enumerate(products):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(product))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(current_stock)))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(min_stock)))
            
            status = "OK" if current_stock >= min_stock else "Bajo"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("green" if status == "OK" else "red"))
            self.inventory_table.setItem(row, 3, status_item)

    def load_sales_table(self):
        sales = [
            (1, "2023-05-01", "Juan Pérez", 150.00, "Completada"),
            (2, "2023-05-02", "María García", 200.50, "Completada"),
            (3, "2023-05-03", "Carlos Rodríguez", 75.25, "Pendiente"),
            (4, "2023-05-04", "Ana Martínez", 300.00, "Completada"),
            (5, "2023-05-05", "Luis Sánchez", 180.75, "Completada")
        ]

        self.sales_table.setRowCount(len(sales))
        for row, (id, date, customer, total, status) in enumerate(sales):
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.sales_table.setItem(row, 1, QTableWidgetItem(date))
            self.sales_table.setItem(row, 2, QTableWidgetItem(customer))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"${total:.2f}"))
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("green" if status == "Completada" else "orange"))
            self.sales_table.setItem(row, 4, status_item)

    def apply_sales_filters(self):
        # Aquí iría la lógica para aplicar los filtros de fecha a la tabla de ventas
        QMessageBox.information(self, "Filtros Aplicados", "Los filtros de fecha han sido aplicados.")
        self.load_sales_table()  # Recargar la tabla con los nuevos filtros

    def show_update_inventory_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Actualizar Inventario")
        layout = QFormLayout(dialog)

        product_input = QLineEdit(dialog)
        quantity_input = QLineEdit(dialog)
        
        layout.addRow("Producto:", product_input)
        layout.addRow("Nueva Cantidad:", quantity_input)

        buttons = QHBoxLayout()
        save_button = QPushButton("Guardar")
        cancel_button = QPushButton("Cancelar")
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)

        layout.addRow(buttons)

        save_button.clicked.connect(lambda: self.update_inventory(product_input.text(), quantity_input.text(), dialog))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

    def update_inventory(self, product, quantity, dialog):
        try:
            quantity = int(quantity)
            # Aquí iría la lógica para actualizar el inventario en la base de datos
            QMessageBox.information(self, "Éxito", f"Inventario actualizado para {product}: {quantity} unidades")
            dialog.accept()
            self.load_inventory()  # Recargar la tabla de inventario
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor, ingrese una cantidad válida.")