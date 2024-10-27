from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QGroupBox,
    QPushButton,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QProgressBar,
    QScrollArea,
    QTabWidget,
    QCalendarWidget,
    QDialog,
    QFormLayout,
    QGridLayout,
    QMessageBox,
    QApplication,
)
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import sqlite3
from datetime import datetime, timedelta


class DashboardModule(QWidget):
    refresh_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
        self.refresh_signal.connect(self.load_data)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.load_data)
        self.update_timer.start(300000)  # 300000 ms = 5 minutos

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.setStyleSheet(
            """
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
        """
        )

        self.title_label = QLabel("Dashboard de Ventas")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title_label.setStyleSheet(
            """
            color: #2c3e50;
            margin: 10px 0;
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9);
            border-radius: 10px;
            padding: 10px;
            color: white;
        """
        )
        main_layout.addWidget(self.title_label)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
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
        """
        )
        self.tab_widget.addTab(self.create_overview_tab(), "Resumen")
        self.tab_widget.addTab(self.create_sales_tab(), "Ventas")
        self.tab_widget.addTab(
            self.create_products_inventory_tab(), "Productos e Inventario"
        )
        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

    def create_overview_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.create_sales_summary())
        layout.addWidget(self.create_sales_chart())
        layout.addWidget(self.create_kpi_widget())
        layout.addWidget(self.create_new_entities_summary())

        tab.setLayout(layout)
        return tab

    def create_sales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

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

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Fecha", "Total", "Usuario"])
        self.sales_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.sales_table)

        tab.setLayout(layout)
        return tab

    def create_products_inventory_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.create_top_products_table())
        layout.addWidget(self.create_product_stock_chart())

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(3)
        self.inventory_table.setHorizontalHeaderLabels(
            ["Producto", "Stock Actual", "Precio"]
        )
        self.inventory_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.inventory_table)

        tab.setLayout(layout)
        return tab

    def create_sales_summary(self):
        group_box = QGroupBox("Resumen de Ventas")
        layout = QHBoxLayout()

        self.total_sales_label = QLabel("Total de Ventas: $0")
        self.total_sales_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.total_sales_label)

        self.today_sales_label = QLabel("Ventas de Hoy: $0")
        self.today_sales_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.today_sales_label)

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

    def create_kpi_widget(self):
        group_box = QGroupBox("KPIs")
        group_box.setObjectName("KPIs")
        layout = QGridLayout()

        kpis = [
            ("Ticket Promedio", "$0"),
            ("Productos Únicos", "0"),
            ("Usuarios Activos", "0"),
            ("Productos por Venta", "0"),
        ]

        for i, (kpi_name, kpi_value) in enumerate(kpis):
            name_label = QLabel(kpi_name)
            value_label = QLabel(kpi_value)
            value_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            layout.addWidget(name_label, i // 2, (i % 2) * 2)
            layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)

        group_box.setLayout(layout)
        return group_box

    def create_new_entities_summary(self):
        group_box = QGroupBox("Resumen de Clientes y Proveedores")
        layout = QHBoxLayout()

        self.new_customers_label = QLabel("Total de Clientes: 0")
        self.new_customers_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.new_customers_label)

        self.new_suppliers_label = QLabel("Total de Proveedores: 0")
        self.new_suppliers_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.new_suppliers_label)

        group_box.setLayout(layout)
        return group_box

    def create_top_products_table(self):
        group_box = QGroupBox("Productos Más Vendidos")
        layout = QVBoxLayout()

        self.top_products_table = QTableWidget(5, 3)
        self.top_products_table.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Total Ventas"]
        )
        self.top_products_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
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

    def load_data(self):
        self.load_sales_summary()
        self.load_sales_chart()
        self.load_kpis()
        self.load_top_products()
        self.load_product_stock_chart()
        self.load_inventory()
        self.load_sales_table()
        self.load_new_entities_summary()

    def load_sales_summary(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        c.execute("SELECT SUM(total) FROM ventas")
        total_sales = c.fetchone()[0] or 0

        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ?", (f"{today}%",))
        today_sales = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(*) FROM ventas")
        transactions = c.fetchone()[0] or 0

        conn.close()

        self.total_sales_label.setText(f"Total de Ventas: ${total_sales:.2f}")
        self.today_sales_label.setText(f"Ventas de Hoy: ${today_sales:.2f}")
        self.transactions_label.setText(f"Transacciones: {transactions}")

    def load_sales_chart(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        c.execute(
            """
            SELECT strftime('%Y-%m', fecha) as month, SUM(total) as total_sales
            FROM ventas
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
        """
        )
        results = c.fetchall()
        conn.close()

        months = [row[0] for row in results][::-1]
        sales = [row[1] for row in results][::-1]

        fig = go.Figure(data=[go.Bar(x=months, y=sales)])
        fig.update_layout(
            title="Ventas Mensuales", xaxis_title="Mes", yaxis_title="Ventas ($)"
        )

        plot(fig, filename="sales_chart.html", auto_open=False)
        self.sales_chart_widget.setText(
            '<img src="sales_chart.html" width="100%" height="300">'
        )

    def load_kpis(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        # Ticket Promedio
        c.execute("SELECT AVG(total) FROM ventas")
        avg_ticket = c.fetchone()[0] or 0

        # Productos Únicos
        c.execute("SELECT COUNT(DISTINCT id) FROM productos")
        unique_products = c.fetchone()[0] or 0

        # Usuarios Activos
        c.execute("SELECT COUNT(DISTINCT user_id) FROM ventas")
        active_users = c.fetchone()[0] or 0

        # Productos por Venta
        c.execute(
            """
            SELECT AVG(product_count) FROM (
                SELECT venta_id, COUNT(*) as product_count
                FROM detalles_venta
                GROUP BY venta_id
            )
        """
        )
        products_per_sale = c.fetchone()[0] or 0

        conn.close()

        kpi_group_box = self.findChild(QGroupBox, "KPIs")
        if kpi_group_box:
            kpi_layout = kpi_group_box.layout()
            if kpi_layout:
                kpi_layout.itemAtPosition(0, 1).widget().setText(f"${avg_ticket:.2f}")
                kpi_layout.itemAtPosition(0, 3).widget().setText(f"{unique_products}")
                kpi_layout.itemAtPosition(1, 1).widget().setText(f"{active_users}")
                kpi_layout.itemAtPosition(1, 3).widget().setText(
                    f"{products_per_sale:.1f}"
                )

    def load_top_products(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        c.execute(
            """
            SELECT p.nombre, SUM(dv.cantidad) as total_quantity, SUM(dv.cantidad * dv.precio) as total_sales
            FROM detalles_venta dv
            JOIN productos p ON dv.producto_id = p.id
            GROUP BY dv.producto_id
            ORDER BY total_sales DESC
            LIMIT 5
        """
        )
        results = c.fetchall()
        conn.close()

        for row, (product, quantity, total) in enumerate(results):
            self.top_products_table.setItem(row, 0, QTableWidgetItem(product))
            self.top_products_table.setItem(row, 1, QTableWidgetItem(str(quantity)))

            # Manejar el caso donde 'total' podría ser None
            if total is None:
                total_str = "$0.00"  # Valor predeterminado
            else:
                total_str = f"${total:.2f}"  # Formato adecuado

            self.top_products_table.setItem(row, 2, QTableWidgetItem(total_str))

    def load_product_stock_chart(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        c.execute(
            """
            SELECT nombre, stock
            FROM productos
            ORDER BY stock DESC
            LIMIT 5
        """
        )
        results = c.fetchall()
        conn.close()

        products = [row[0] for row in results]
        stock = [row[1] for row in results]

        fig = go.Figure(data=[go.Bar(x=products, y=stock)])
        fig.update_layout(
            title="Stock de Productos",
            xaxis_title="Producto",
            yaxis_title="Unidades en Stock",
        )

        plot(fig, filename="stock_chart.html", auto_open=False)
        self.stock_chart_widget.setText(
            '<img src="stock_chart.html" width="100%" height="300">'
        )

    def load_inventory(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        c.execute(
            """
            SELECT nombre, stock, precio
            FROM productos
            ORDER BY stock ASC
        """
        )
        results = c.fetchall()
        conn.close()

        self.inventory_table.setRowCount(len(results))
        for row, (product, stock, price) in enumerate(results):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(product))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(stock)))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(f"${price:.2f}"))

    def load_sales_table(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        c.execute(
            """
            SELECT v.id, v.fecha, v.total, u.username
            FROM ventas v
            JOIN usuarios u ON v.user_id = u.id
            ORDER BY v.fecha DESC
            LIMIT 50
        """
        )
        results = c.fetchall()
        conn.close()

        self.sales_table.setRowCount(len(results))
        for row, (id, date, total, username) in enumerate(results):
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.sales_table.setItem(row, 1, QTableWidgetItem(date))
            self.sales_table.setItem(row, 2, QTableWidgetItem(f"${total:.2f}"))
            self.sales_table.setItem(row, 3, QTableWidgetItem(username))

    def load_new_entities_summary(self):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        # Contar todos los clientes (ya que no tenemos una columna de fecha de creación)
        c.execute("SELECT COUNT(*) FROM clientes")
        total_customers = c.fetchone()[0] or 0

        # Contar todos los proveedores (ya que no tenemos una columna de fecha de creación)
        c.execute("SELECT COUNT(*) FROM proveedores")
        total_suppliers = c.fetchone()[0] or 0

        conn.close()

        self.new_customers_label.setText(f"Total de Clientes: {total_customers}")
        self.new_suppliers_label.setText(f"Total de Proveedores: {total_suppliers}")
    def apply_sales_filters(self):
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()

        c.execute(
            """
            SELECT v.id, v.fecha, v.total, u.username
            FROM ventas v
            JOIN usuarios u ON v.user_id = u.id
            WHERE v.fecha BETWEEN ? AND ?
            ORDER BY v.fecha DESC
        """,
            (date_from, date_to),
        )
        results = c.fetchall()
        conn.close()

        self.sales_table.setRowCount(len(results))
        for row, (id, date, total, username) in enumerate(results):
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.sales_table.setItem(row, 1, QTableWidgetItem(date))
            self.sales_table.setItem(row, 2, QTableWidgetItem(f"${total:.2f}"))
            self.sales_table.setItem(row, 3, QTableWidgetItem(username))

        QMessageBox.information(
            self, "Filtros Aplicados", "Los filtros de fecha han sido aplicados."
        )
