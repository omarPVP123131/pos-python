import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox,
    QHeaderView, QSpinBox, QDoubleSpinBox, QFileDialog, QScrollArea,
    QGridLayout, QFrame, QDialog, QFormLayout, QDialogButtonBox, QMenu
)
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction
from PyQt6.QtCore import Qt, pyqtSignal

class ProductWidget(QFrame):
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)

    def __init__(self, product_data):
        super().__init__()
        self.product_data = product_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
        """)

        # Imagen del producto
        image_label = QLabel()
        pixmap = QPixmap(self.product_data[5]).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label)

        # Nombre del producto
        name_label = QLabel(self.product_data[1])
        name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Precio
        price_label = QLabel(f"Precio: ${self.product_data[2]:.2f}")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price_label)

        # Stock
        stock_label = QLabel(f"Stock: {self.product_data[3]}")
        stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(stock_label)

        # Proveedor
        supplier_label = QLabel(f"Proveedor: {self.product_data[4]}")
        supplier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(supplier_label)

        # Botones de editar y eliminar
        button_layout = QHBoxLayout()
        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(lambda: self.edit_clicked.emit(self.product_data[0]))
        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(lambda: self.delete_clicked.emit(self.product_data[0]))
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

class InventoryModule(QWidget):
    inventory_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
        self.load_suppliers()
        self.image_path = None

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Estilo general
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: #333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                margin: 4px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)

        # Barra lateral izquierda
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)

        # Título
        title = QLabel("Gestión de Inventario")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ecf0f1; margin: 20px 0;")
        sidebar_layout.addWidget(title)

        # Formulario de entrada
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nombre del producto")
        sidebar_layout.addWidget(self.product_name_input)

        self.product_price_input = QDoubleSpinBox()
        self.product_price_input.setRange(0, 1000000)
        self.product_price_input.setPrefix("$")
        self.product_price_input.setDecimals(2)
        sidebar_layout.addWidget(self.product_price_input)

        self.product_stock_input = QSpinBox()
        self.product_stock_input.setRange(0, 1000000)
        sidebar_layout.addWidget(self.product_stock_input)

        self.supplier_combo = QComboBox()
        sidebar_layout.addWidget(self.supplier_combo)

        self.image_button = QPushButton("Seleccionar imagen")
        self.image_button.setIcon(QIcon("icons/add.png"))
        self.image_button.clicked.connect(self.select_image)
        sidebar_layout.addWidget(self.image_button)

        self.add_product_button = QPushButton("Agregar producto")
        self.add_product_button.setIcon(QIcon("icons/add.png"))
        self.add_product_button.clicked.connect(self.add_product)
        sidebar_layout.addWidget(self.add_product_button)

        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)

        # Área principal de productos
        product_area = QScrollArea()
        product_area.setWidgetResizable(True)
        product_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ecf0f1;
            }
        """)

        self.product_grid = QGridLayout()
        self.product_grid.setSpacing(20)

        product_widget = QWidget()
        product_widget.setLayout(self.product_grid)
        product_area.setWidget(product_widget)

        main_layout.addWidget(product_area, 1)

    def select_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Archivos de imagen (*.png *.jpg *.jpeg)")
        if image_path:
            self.image_path = image_path
            QMessageBox.information(self, "Imagen seleccionada", f"Imagen seleccionada: {os.path.basename(image_path)}")

    def add_product(self):
        name = self.product_name_input.text()
        price = self.product_price_input.value()
        stock = self.product_stock_input.value()
        supplier_id = self.supplier_combo.currentData()

        if not name or not self.image_path:
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos e incluya una imagen.")
            return

        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("INSERT INTO productos (nombre, precio, stock, proveedor_id, imagen) VALUES (?, ?, ?, ?, ?)",
                      (name, price, stock, supplier_id, self.image_path))
            conn.commit()
            conn.close()

            self.clear_inputs()
            self.load_products()
            self.inventory_updated.emit()
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el producto: {e}")

    def clear_inputs(self):
        self.product_name_input.clear()
        self.product_price_input.setValue(0)
        self.product_stock_input.setValue(0)
        self.image_path = None

    def load_products(self):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("""
                SELECT p.id, p.nombre, p.precio, p.stock, COALESCE(pr.nombre, 'Sin proveedor'), p.imagen
                FROM productos p
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            """)
            products = c.fetchall()
            conn.close()

            # Limpiar el grid existente
            for i in reversed(range(self.product_grid.count())): 
                self.product_grid.itemAt(i).widget().setParent(None)

            # Agregar productos al grid
            for i, product in enumerate(products):
                product_widget = ProductWidget(product)
                product_widget.edit_clicked.connect(self.edit_product)
                product_widget.delete_clicked.connect(self.delete_product)
                row = i // 3
                col = i % 3
                self.product_grid.addWidget(product_widget, row, col)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los productos: {e}")

    def load_suppliers(self):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT id, nombre FROM proveedores")
            suppliers = c.fetchall()
            conn.close()

            self.supplier_combo.clear()
            self.supplier_combo.addItem("Seleccione un proveedor", None)
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier[1], supplier[0])

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los proveedores: {e}")

    def edit_product(self, product_id):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT nombre, precio, stock, proveedor_id, imagen FROM productos WHERE id = ?", (product_id,))
            product = c.fetchone()
            conn.close()

            if product:
                dialog = QDialog(self)
                dialog.setWindowTitle("Editar Producto")
                layout = QFormLayout(dialog)

                name_input = QLineEdit(product[0])
                price_input = QDoubleSpinBox()
                price_input.setRange(0, 1000000)
                price_input.setPrefix("$")
                price_input.setDecimals(2)
                price_input.setValue(product[1])
                stock_input = QSpinBox()
                stock_input.setRange(0, 1000000)
                stock_input.setValue(product[2])
                supplier_combo = QComboBox()

                # Ruta de la imagen original
                image_path = product[4]
                # Bandera para controlar si la imagen ha cambiado
                self.image_changed = False

                layout.addRow("Nombre:", name_input)
                layout.addRow("Precio:", price_input)
                layout.addRow("Stock:", stock_input)
                layout.addRow("Proveedor:", supplier_combo)

                # Botón para cambiar la imagen
                image_button = QPushButton("Cambiar imagen")
                image_button.clicked.connect(lambda: self.change_image(image_path, lambda new_image_path: self.set_image_path(new_image_path)))
                layout.addRow("Imagen:", image_button)

                buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                    Qt.Orientation.Horizontal,
                    dialog
                )
                layout.addRow(buttons)

                buttons.accepted.connect(dialog.accept)
                buttons.rejected.connect(dialog.reject)

                # Cargar proveedores en el combo
                self.load_suppliers_for_combo(supplier_combo, product[3])

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_name = name_input.text()
                    new_price = price_input.value()
                    new_stock = stock_input.value()
                    new_supplier_id = supplier_combo.currentData()

                    # Solo actualizar la imagen si fue cambiada
                    if not self.image_changed:
                        self.image_path = image_path

                    self.update_product(product_id, new_name, new_price, new_stock, new_supplier_id, self.image_path)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el producto para editar: {e}")


    def change_image(self, current_image_path, callback):
        new_image_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar nueva imagen", "", "Archivos de imagen (*.png *.jpg *.jpeg)")
        if new_image_path:
            # Callback para actualizar la ruta de la imagen
            callback(new_image_path)
            return new_image_path
        return current_image_path

    def set_image_path(self, new_image_path):
        self.image_path = new_image_path
        self.image_changed = True  # Marcar que la imagen ha cambiado

    def load_suppliers_for_combo(self, combo, current_supplier_id):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT id, nombre FROM proveedores")
            suppliers = c.fetchall()
            conn.close()

            combo.clear()
            combo.addItem("Seleccione un proveedor", None)
            for supplier in suppliers:
                combo.addItem(supplier[1], supplier[0])
                if supplier[0] == current_supplier_id:
                    combo.setCurrentIndex(combo.count() - 1)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los proveedores: {e}")

    def update_product(self, product_id, name, price, stock, supplier_id, image_path):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("""
                UPDATE productos
                SET nombre = ?, precio = ?, stock = ?, proveedor_id = ?, imagen = ?
                WHERE id = ?
            """, (name, price, stock, supplier_id, image_path, product_id))
            conn.commit()
            conn.close()

            self.load_products()
            self.inventory_updated.emit()
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto: {e}")

    def delete_product(self, product_id):
        reply = QMessageBox.question(self, "Confirmar eliminación",
                                     "¿Está seguro de que desea eliminar este producto?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('pos_database.db')
                c = conn.cursor()
                c.execute("DELETE FROM productos WHERE id = ?", (product_id,))
                conn.commit()
                conn.close()

                self.load_products()
                self.inventory_updated.emit()
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    inventory_module = InventoryModule()
    inventory_module.setGeometry(100, 100, 1200, 800)
    inventory_module.show()
    sys.exit(app.exec())