from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox, QApplication
)
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import sqlite3
import sys

class SuppliersModule(QWidget):
    supplier_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_suppliers()

    def init_ui(self):
        layout = QVBoxLayout()
        #colores                 #4a90e2 #357ae8;

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
            QLineEdit {
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
        title = QLabel("Gestión de Proveedores")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #4a90e2; margin: 10px 0;")
        layout.addWidget(title)

        # Formulario de entrada
        form_layout = QHBoxLayout()
        
        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Nombre del proveedor")
        self.supplier_contact_input = QLineEdit()
        self.supplier_contact_input.setPlaceholderText("Contacto")
        self.supplier_phone_input = QLineEdit()
        self.supplier_phone_input.setPlaceholderText("Teléfono")
        self.supplier_email_input = QLineEdit()
        self.supplier_email_input.setPlaceholderText("Email")
        
        self.add_supplier_button = QPushButton("Agregar proveedor")
        self.add_supplier_button.setIcon(QIcon("icons/add.png"))
        self.add_supplier_button.clicked.connect(self.add_supplier)

        form_layout.addWidget(self.supplier_name_input)
        form_layout.addWidget(self.supplier_contact_input)
        form_layout.addWidget(self.supplier_phone_input)
        form_layout.addWidget(self.supplier_email_input)
        form_layout.addWidget(self.add_supplier_button)

        layout.addLayout(form_layout)

        # Tabla de proveedores
        self.supplier_table = QTableWidget(0, 5)
        self.supplier_table.setHorizontalHeaderLabels(["ID", "Nombre", "Contacto", "Teléfono", "Email"])
        self.supplier_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.supplier_table.setAlternatingRowColors(True)
        self.supplier_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d6d9dc;
                selection-background-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.supplier_table)

        # Botones de acción
        button_layout = QHBoxLayout()
        self.edit_supplier_button = QPushButton("Editar proveedor")
        self.edit_supplier_button.setIcon(QIcon("icons/edit.png"))
        self.edit_supplier_button.clicked.connect(self.edit_supplier)
        self.delete_supplier_button = QPushButton("Eliminar proveedor")
        self.delete_supplier_button.setIcon(QIcon("icons/delete.png"))
        self.delete_supplier_button.clicked.connect(self.delete_supplier)

        button_layout.addWidget(self.edit_supplier_button)
        button_layout.addWidget(self.delete_supplier_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_supplier(self):
        name = self.supplier_name_input.text()
        contact = self.supplier_contact_input.text()
        phone = self.supplier_phone_input.text()
        email = self.supplier_email_input.text()

        if not name:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nombre de proveedor.")
            return

        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("INSERT INTO proveedores (nombre, contacto, telefono, email) VALUES (?, ?, ?, ?)",
                      (name, contact, phone, email))
            conn.commit()
            conn.close()

            self.supplier_name_input.clear()
            self.supplier_contact_input.clear()
            self.supplier_phone_input.clear()
            self.supplier_email_input.clear()
            self.load_suppliers()
            self.supplier_updated.emit()

            QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el proveedor: {e}")

    def load_suppliers(self):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT * FROM proveedores")
            suppliers = c.fetchall()
            conn.close()

            self.supplier_table.setRowCount(0)
            for row, supplier in enumerate(suppliers):
                self.supplier_table.insertRow(row)
                for col, value in enumerate(supplier):
                    item = QTableWidgetItem(str(value))
                    if col == 0:  # ID column
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.supplier_table.setItem(row, col, item)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los proveedores: {e}")

    def edit_supplier(self):
        selected_items = self.supplier_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un proveedor para editar.")
            return

        row = selected_items[0].row()
        supplier_id = int(self.supplier_table.item(row, 0).text())
        current_name = self.supplier_table.item(row, 1).text()
        current_contact = self.supplier_table.item(row, 2).text()
        current_phone = self.supplier_table.item(row, 3).text()
        current_email = self.supplier_table.item(row, 4).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Proveedor")
        layout = QFormLayout(dialog)

        name_input = QLineEdit(current_name)
        contact_input = QLineEdit(current_contact)
        phone_input = QLineEdit(current_phone)
        email_input = QLineEdit(current_email)

        layout.addRow("Nombre:", name_input)
        layout.addRow("Contacto:", contact_input)
        layout.addRow("Teléfono:", phone_input)
        layout.addRow("Email:", email_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal,
            dialog
        )
        layout.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = name_input.text()
            new_contact = contact_input.text()
            new_phone = phone_input.text()
            new_email = email_input.text()

            try:
                conn = sqlite3.connect('pos_database.db')
                c = conn.cursor()
                c.execute("""
                    UPDATE proveedores
                    SET nombre = ?, contacto = ?, telefono = ?, email = ?
                    WHERE id = ?
                """, (new_name, new_contact, new_phone, new_email, supplier_id))
                conn.commit()
                conn.close()

                self.load_suppliers()
                self.supplier_updated.emit()
                QMessageBox.information(self, "Éxito", "Proveedor actualizado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el proveedor: {e}")

    def delete_supplier(self):
        selected_items = self.supplier_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un proveedor para eliminar.")
            return

        row = selected_items[0].row()
        supplier_id = int(self.supplier_table.item(row, 0).text())
        supplier_name = self.supplier_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirmar eliminación",
                                     f"¿Está seguro de que desea eliminar el proveedor '{supplier_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('pos_database.db')
                c = conn.cursor()
                c.execute("DELETE FROM proveedores WHERE id = ?", (supplier_id,))
                conn.commit()
                conn.close()

                self.load_suppliers()
                self.supplier_updated.emit()
                QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el proveedor: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    suppliers_module = SuppliersModule()
    suppliers_module.show()
    sys.exit(app.exec())