from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox, QApplication, QComboBox, QDoubleSpinBox,
    QGroupBox, QSplitter, QCompleter, QFrame
)
from PyQt6.QtGui import QFont, QColor, QIcon, QKeySequence, QShortcut, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
import sqlite3
import sys

class POSModule(QWidget):
    sale_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
        self.load_customers()

    def init_ui(self):
        layout = QVBoxLayout()

        # Estilo general mejorado
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                margin: 8px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003d80;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                padding: 12px;
                margin: 6px 0;
                border: 1px solid #ced4da;
                border-radius: 8px;
                background-color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border-color: #80bdff;
                outline: none;
            }
            QTableWidget {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                color: #495057;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
            }
            QGroupBox {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1em;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #495057;
            }
        """)

        # Header con título y logo
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("icons/add.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio))
        header_layout.addWidget(logo_label)

        title = QLabel("Sistema POS")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #007bff; margin-left: 10px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Botón de ayuda
        help_button = QPushButton(QIcon("icons/help.png"), "")
        help_button.setFixedSize(40, 40)
        help_button.setStyleSheet("background-color: transparent; border: none;")
        help_button.clicked.connect(self.show_help)
        header_layout.addWidget(help_button)

        layout.addLayout(header_layout)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #dee2e6;")
        layout.addWidget(line)

        # Contenido principal
        main_layout = QHBoxLayout()

        # Panel izquierdo
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Grupo de cliente
        customer_group = QGroupBox("Datos del cliente")
        customer_group_layout = QVBoxLayout()
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        self.customer_combo.setPlaceholderText("Buscar o seleccionar cliente")
        customer_group_layout.addWidget(self.customer_combo)
        customer_group.setLayout(customer_group_layout)
        left_layout.addWidget(customer_group)

        # Grupo de producto
        product_group = QGroupBox("Agregar producto")
        product_layout = QVBoxLayout()

        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Buscar producto...")
        product_layout.addWidget(self.product_search)

        self.product_combo = QComboBox()
        self.product_combo.setPlaceholderText("Seleccionar producto")
        product_layout.addWidget(self.product_combo)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Cantidad:"))
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.01, 1000)
        self.quantity_input.setValue(1)
        quantity_layout.addWidget(self.quantity_input)
        product_layout.addLayout(quantity_layout)

        self.add_to_cart_button = QPushButton("Agregar al carrito")
        self.add_to_cart_button.setIcon(QIcon("icons/add_to_cart.png"))
        self.add_to_cart_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.add_to_cart_button.clicked.connect(self.add_to_cart)
        product_layout.addWidget(self.add_to_cart_button)

        product_group.setLayout(product_layout)
        left_layout.addWidget(product_group)

        left_layout.addStretch()

        # Panel derecho
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Tabla de carrito
        cart_group = QGroupBox("Carrito de compras")
        cart_layout = QVBoxLayout()
        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Cantidad", "Subtotal"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e9ecef;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        cart_layout.addWidget(self.cart_table)

        # Botón para eliminar productos del carrito
        self.remove_from_cart_button = QPushButton("Eliminar seleccionado")
        self.remove_from_cart_button.setIcon(QIcon("icons/remove.png"))
        self.remove_from_cart_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.remove_from_cart_button.clicked.connect(self.remove_from_cart)
        cart_layout.addWidget(self.remove_from_cart_button)

        cart_group.setLayout(cart_layout)
        right_layout.addWidget(cart_group)

        # Total y botón de venta
        total_layout = QHBoxLayout()
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #28a745;")
        self.complete_sale_button = QPushButton("Completar venta")
        self.complete_sale_button.setIcon(QIcon("icons/complete_sale.png"))
        self.complete_sale_button.setFixedSize(200, 60)
        self.complete_sale_button.setStyleSheet("""
            background-color: #28a745;
            font-size: 16px;
            font-weight: bold;
        """)
        self.complete_sale_button.clicked.connect(self.complete_sale)

        total_layout.addWidget(self.total_label)
        total_layout.addWidget(self.complete_sale_button)
        right_layout.addLayout(total_layout)

        # Agregar paneles al layout principal
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        layout.addLayout(main_layout)

        self.setLayout(layout)

        # Configurar autocompletado
        self.setup_autocomplete()

        # Agregar tooltips
        self.add_tooltips()

        # Implementar atajos de teclado
        self.add_shortcuts()


    def add_tooltips(self):
        self.customer_combo.setToolTip("Buscar o seleccionar un cliente")
        self.product_search.setToolTip("Buscar un producto por nombre o código")
        self.product_combo.setToolTip("Seleccionar un producto de la lista")
        self.quantity_input.setToolTip("Especificar la cantidad del producto")
        self.add_to_cart_button.setToolTip("Agregar el producto seleccionado al carrito (Ctrl+A)")
        self.remove_from_cart_button.setToolTip("Eliminar el producto seleccionado del carrito (Ctrl+R)")
        self.complete_sale_button.setToolTip("Finalizar la venta y guardar en la base de datos (Ctrl+F)")

    def add_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+A"), self, self.add_to_cart)
        QShortcut(QKeySequence("Ctrl+F"), self, self.complete_sale)
        QShortcut(QKeySequence("Ctrl+R"), self, self.remove_from_cart)
        QShortcut(QKeySequence("Ctrl+P"), self, lambda: self.product_search.setFocus())
        QShortcut(QKeySequence("Ctrl+C"), self, lambda: self.customer_combo.setFocus())
        QShortcut(QKeySequence("Ctrl+Q"), self, lambda: self.quantity_input.setFocus())
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_help)

    def setup_autocomplete(self):
        # Autocompletado para productos
        self.product_completer = QCompleter()
        self.product_completer.setModel(self.product_combo.model())
        self.product_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.product_search.setCompleter(self.product_completer)

        # Autocompletado para clientes
        self.customer_completer = QCompleter()
        self.customer_completer.setModel(self.customer_combo.model())
        self.customer_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.customer_combo.setCompleter(self.customer_completer)

    def show_help(self):
        help_text = """
        Bienvenido al Sistema POS

        Instrucciones rápidas:
        1. Seleccione un cliente o búsquelo en el campo correspondiente.
        2. Para agregar productos al carrito:
        - Busque el producto en el campo de búsqueda.
        - Seleccione el producto de la lista desplegable.
        - Ajuste la cantidad si es necesario.
        - Haga clic en "Agregar al carrito".
        3. Para eliminar productos del carrito, selecciónelos y haga clic en "Eliminar seleccionado".
        4. Una vez que haya terminado, haga clic en "Completar venta".

        Atajos de teclado:
        Ctrl+A: Agregar al carrito
        Ctrl+F: Completar venta
        Ctrl+R: Eliminar del carrito
        Ctrl+P: Enfocar búsqueda de productos
        Ctrl+C: Enfocar selección de cliente
        Ctrl+Q: Enfocar entrada de cantidad
        Ctrl+H: Mostrar esta ayuda
        """
        QMessageBox.information(self, "Ayuda del Sistema POS", help_text)
                                
    def focus_product_search(self):
        self.product_search.setFocus()

    def focus_customer_combo(self):
        self.customer_combo.setFocus()

    def focus_quantity_input(self):
        self.quantity_input.setFocus()

    def show_shortcuts_help(self):
        shortcuts_text = """
        Atajos de teclado:
        Ctrl+A: Agregar al carrito
        Ctrl+F: Completar venta
        Ctrl+R: Eliminar del carrito
        Ctrl+P: Enfocar búsqueda de productos
        Ctrl+C: Enfocar selección de cliente
        Ctrl+Q: Enfocar entrada de cantidad
        Ctrl+S: Mostrar esta ayuda
        """
        QMessageBox.information(self, "Atajos de teclado", shortcuts_text)
        
        
    def add_product_search(self):
        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Buscar producto...")
        self.product_search.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.product_search)
        return search_layout

    def filter_products(self, text):
        for i in range(self.product_combo.count()):
            item = self.product_combo.itemText(i)
            self.product_combo.setItemVisible(i, text.lower() in item.lower())

    def remove_from_cart(self):
        selected_rows = set(index.row() for index in self.cart_table.selectedIndexes())
        for row in sorted(selected_rows, reverse=True):
            self.cart_table.removeRow(row)
        self.update_total()


    def load_products(self):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT id, nombre, precio FROM productos")
            products = c.fetchall()
            conn.close()

            self.product_combo.clear()
            product_names = []
            for product in products:
                self.product_combo.addItem(f"{product[1]} - ${product[2]:.2f}", product[0])
                product_names.append(product[1])

            # Configurar el autocompletado de productos
            self.product_completer.setModel(self.product_combo.model())
            self.product_completer.setFilterMode(Qt.MatchFlag.MatchContains)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los productos: {e}")

    def load_customers(self):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT id, nombre FROM clientes")
            customers = c.fetchall()
            conn.close()

            self.customer_combo.clear()
            customer_names = []
            for customer in customers:
                self.customer_combo.addItem(customer[1], customer[0])
                customer_names.append(customer[1])

            # Configurar el autocompletado de clientes
            self.customer_completer.setModel(self.customer_combo.model())
            self.customer_completer.setFilterMode(Qt.MatchFlag.MatchContains)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los clientes: {e}")

    def add_to_cart(self):
        product_id = self.product_combo.currentData()
        quantity = self.quantity_input.value()

        if not product_id:
            self.show_error_animation(self.product_combo)
            QMessageBox.warning(self, "Error", "Por favor, seleccione un producto.")
            return

        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT nombre, precio FROM productos WHERE id = ?", (product_id,))
            product = c.fetchone()
            conn.close()

            if product:
                name, price = product
                subtotal = price * quantity

                row = self.cart_table.rowCount()
                self.cart_table.insertRow(row)
                self.cart_table.setItem(row, 0, QTableWidgetItem(str(product_id)))
                self.cart_table.setItem(row, 1, QTableWidgetItem(name))
                self.cart_table.setItem(row, 2, QTableWidgetItem(f"${price:.2f}"))
                self.cart_table.setItem(row, 3, QTableWidgetItem(str(quantity)))
                self.cart_table.setItem(row, 4, QTableWidgetItem(f"${subtotal:.2f}"))

                self.update_total()
            else:
                QMessageBox.warning(self, "Error", "Producto no encontrado.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el producto al carrito: {e}")

    def update_total(self):
        total = 0
        for row in range(self.cart_table.rowCount()):
            subtotal = float(self.cart_table.item(row, 4).text().replace('$', ''))
            total += subtotal
        self.total_label.setText(f"Total: ${total:.2f}")

    def complete_sale(self):
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "El carrito está vacío.")
            return

        if not self.confirm_sale():
            return

        customer_id = self.customer_combo.currentData()
        if not customer_id:
            # Asignar cliente "variado" por defecto
            customer_id = self.get_or_create_default_customer()

        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()

            # Calcular el total de la venta
            total_venta = sum(float(self.cart_table.item(row, 4).text().replace('$', '')) for row in range(self.cart_table.rowCount()))

            # Crear la venta con el total calculado
            c.execute("INSERT INTO ventas (cliente_id, fecha, total) VALUES (?, datetime('now'), ?)", (customer_id, total_venta))
            sale_id = c.lastrowid

            # Agregar detalles de la venta
            for row in range(self.cart_table.rowCount()):
                product_id = int(self.cart_table.item(row, 0).text())
                quantity = float(self.cart_table.item(row, 3).text())
                price_unitario = float(self.cart_table.item(row, 2).text().replace('$', ''))
                precio_total = quantity * price_unitario

                c.execute("""
                    INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, precio)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, product_id, quantity, price_unitario, precio_total))

                # Actualizar el stock del producto
                c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (quantity, product_id))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Venta completada correctamente.")
            self.cart_table.setRowCount(0)
            self.update_total()
            self.sale_completed.emit()
            self.show_sale_summary(sale_id)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo completar la venta: {e}")

    def get_or_create_default_customer(self):
        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        
        # Buscar el cliente "variado"
        c.execute("SELECT id FROM clientes WHERE nombre = 'variado'")
        result = c.fetchone()
        
        if result:
            default_customer_id = result[0]
        else:
            # Crear el cliente "variado" si no existe
            c.execute("INSERT INTO clientes (nombre) VALUES ('variado')")
            default_customer_id = c.lastrowid
            conn.commit()
        
        conn.close()
        return default_customer_id


    def show_error_animation(self, widget):
        animation = QPropertyAnimation(widget, b"styleSheet")
        animation.setDuration(300)
        animation.setKeyValueAt(0, "border: 2px solid red;")
        animation.setKeyValueAt(0.5, "border: 2px solid transparent;")
        animation.setKeyValueAt(1, "border: 1px solid #ddd;")
        animation.start()

    def confirm_sale(self):
        confirm = QMessageBox.question(
            self, "Confirmar Venta",
            "¿Está seguro de que desea completar esta venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return confirm == QMessageBox.StandardButton.Yes

    def show_sale_summary(self, sale_id):
        summary = QMessageBox(self)
        summary.setWindowTitle("Resumen de Venta")
        summary.setIcon(QMessageBox.Icon.Information)

        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("""
            SELECT v.id, c.nombre, v.fecha, SUM(d.cantidad * d.precio_unitario) as total
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            JOIN detalles_venta d ON v.id = d.venta_id
            WHERE v.id = ?
            GROUP BY v.id
        """, (sale_id,))
        venta = c.fetchone()

        if venta:
            summary_text = f"""
            Venta #{venta[0]}
            Cliente: {venta[1]}
            Fecha: {venta[2]}
            Total: ${venta[3]:.2f}

            Detalles:
            """

            c.execute("""
                SELECT p.nombre, d.cantidad, d.precio_unitario, (d.cantidad * d.precio_unitario) as subtotal
                FROM detalles_venta d
                JOIN productos p ON d.producto_id = p.id
                WHERE d.venta_id = ?
            """, (sale_id,))
            detalles = c.fetchall()

            for detalle in detalles:
                summary_text += f"\n{detalle[0]}: {detalle[1]} x ${detalle[2]:.2f} = ${detalle[3]:.2f}"

            summary.setText(summary_text)
            summary.exec()

        conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = POSModule()
    window.show()
    sys.exit(app.exec())