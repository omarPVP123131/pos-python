from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QHeaderView,
    QSpinBox, QDoubleSpinBox, QDialog, QFormLayout, QDialogButtonBox, QFileDialog,
    QApplication
)
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import sqlite3
import sys
import os

class InventoryModule(QWidget):
    inventory_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
        self.load_suppliers()
        self.image_path = None  # Para almacenar la ruta de la imagen seleccionada

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Estilo general
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
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
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #4a90e2;
                color: white;
                padding: 8px;
                border: 1px solid #357ae8;
            }
        """)

        # Título
        title = QLabel("Gestión de Inventario")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #4a90e2; margin: 10px 0;")
        layout.addWidget(title)

        # Formulario de entrada
        form_layout = QHBoxLayout()
        
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nombre del producto")
        
        self.product_price_input = QDoubleSpinBox()
        self.product_price_input.setRange(0, 1000000)
        self.product_price_input.setPrefix("$")
        self.product_price_input.setDecimals(2)
        
        self.product_stock_input = QSpinBox()
        self.product_stock_input.setRange(0, 1000000)
        
        self.supplier_combo = QComboBox()
        
        self.add_product_button = QPushButton("Agregar producto")
        self.add_product_button.setIcon(QIcon("icons/add.png"))
        self.add_product_button.clicked.connect(self.add_product)

        # Botón para seleccionar imagen
        self.image_button = QPushButton("Seleccionar imagen")
        self.image_button.clicked.connect(self.select_image)

        self.add_product_button = QPushButton("Agregar producto")
        self.add_product_button.setIcon(QIcon("icons/add.png"))
        self.add_product_button.clicked.connect(self.add_product)

        form_layout.addWidget(self.product_name_input)
        form_layout.addWidget(self.product_price_input)
        form_layout.addWidget(self.product_stock_input)
        form_layout.addWidget(self.supplier_combo)
        form_layout.addWidget(self.image_button)
        form_layout.addWidget(self.add_product_button)

        layout.addLayout(form_layout)

        # Tabla de productos
        self.product_table = QTableWidget(0, 5)
        self.product_table.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Stock", "Proveedor"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d6d9dc;
                selection-background-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.product_table)

        # Botones de acción
        button_layout = QHBoxLayout()
        self.edit_product_button = QPushButton("Editar producto")
        self.edit_product_button.setIcon(QIcon("icons/edit.png"))
        self.edit_product_button.clicked.connect(self.edit_product)
        self.delete_product_button = QPushButton("Eliminar producto")
        self.delete_product_button.setIcon(QIcon("icons/delete.png"))
        self.delete_product_button.clicked.connect(self.delete_product)

        button_layout.addWidget(self.edit_product_button)
        button_layout.addWidget(self.delete_product_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_image(self):
        # Abre el explorador de archivos y almacena la ruta de la imagen seleccionada
        image_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Archivos de imagen (*.png *.jpg *.jpeg)")
        if image_path:
            self.image_path = image_path
            QMessageBox.information(self, "Imagen seleccionada", f"Imagen seleccionada: {os.path.basename(image_path)}")

    def add_product(self):
        name = self.product_name_input.text()
        price = self.product_price_input.value()
        stock = self.product_stock_input.value()
        supplier_id = self.supplier_combo.currentData()

        if not name:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nombre de producto.")
            return

        if not self.image_path:
            QMessageBox.warning(self, "Error", "Por favor, seleccione una imagen.")
            return

        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("INSERT INTO productos (nombre, precio, stock, proveedor_id, imagen) VALUES (?, ?, ?, ?, ?)",
                      (name, price, stock, supplier_id, self.image_path))
            conn.commit()
            conn.close()

            self.product_name_input.clear()
            self.product_price_input.setValue(0)
            self.product_stock_input.setValue(0)
            self.image_path = None  # Resetear la ruta de la imagen
            self.load_products()
            self.inventory_updated.emit()

            QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el producto: {e}")

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

            self.product_table.setRowCount(0)
            for row, product in enumerate(products):
                self.product_table.insertRow(row)
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    if col == 0:  # ID column
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.product_table.setItem(row, col, item)

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


    def edit_product(self):
        selected_items = self.product_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un producto para editar.")
            return

        row = selected_items[0].row()
        product_id = int(self.product_table.item(row, 0).text())
        current_name = self.product_table.item(row, 1).text()
        current_price = float(self.product_table.item(row, 2).text())
        current_stock = int(self.product_table.item(row, 3).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Producto")
        layout = QFormLayout(dialog)

        name_input = QLineEdit(current_name)
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 1000000)
        price_input.setPrefix("$")
        price_input.setDecimals(2)
        price_input.setValue(current_price)
        stock_input = QSpinBox()
        stock_input.setRange(0, 1000000)
        stock_input.setValue(current_stock)
        supplier_combo = QComboBox()

        layout.addRow("Nombre:", name_input)
        layout.addRow("Precio:", price_input)
        layout.addRow("Stock:", stock_input)
        layout.addRow("Proveedor:", supplier_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal,
            dialog
        )
        layout.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        # Cargar proveedores en el combo
        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM proveedores")
        suppliers = c.fetchall()
        conn.close()

        supplier_combo.addItem("Seleccione un proveedor", None)
        for supplier in suppliers:
            supplier_combo.addItem(supplier[1], supplier[0])

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = name_input.text()
            new_price = price_input.value()
            new_stock = stock_input.value()
            new_supplier_id = supplier_combo.currentData()

            try:
                conn = sqlite3.connect('pos_database.db')
                c = conn.cursor()
                c.execute("""
                    UPDATE productos
                    SET nombre = ?, precio = ?, stock = ?, proveedor_id = ?
                    WHERE id = ?
                """, (new_name, new_price, new_stock, new_supplier_id, product_id))
                conn.commit()
                conn.close()

                self.load_products()
                self.inventory_updated.emit()
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto: {e}")

    def delete_product(self):
        selected_items = self.product_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un producto para eliminar.")
            return

        row = selected_items[0].row()
        product_id = int(self.product_table.item(row, 0).text())
        product_name = self.product_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirmar eliminación",
                                     f"¿Está seguro de que desea eliminar el producto '{product_name}'?",
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
    inventory_module.show()
    sys.exit(app.exec())