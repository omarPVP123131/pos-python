from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox, QApplication, QFrame, QSplitter
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
        main_layout = QHBoxLayout(self)

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
        
        # Ajustar el espaciado entre widgets y márgenes generales del layout
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Panel izquierdo
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)  # Espaciado entre widgets en el panel izquierdo

        # Título
        title = QLabel("Gestión de Proveedores")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #3498DB; margin: 20px 0;")
        left_layout.addWidget(title)

        # Formulario de entrada
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)  # Espaciado entre campos del formulario
        form_layout.setContentsMargins(0, 10, 0, 10)

        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Nombre del proveedor")
        self.supplier_contact_input = QLineEdit()
        self.supplier_contact_input.setPlaceholderText("Contacto")
        self.supplier_phone_input = QLineEdit()
        self.supplier_phone_input.setPlaceholderText("Teléfono")
        self.supplier_email_input = QLineEdit()
        self.supplier_email_input.setPlaceholderText("Email")

        form_layout.addRow("Nombre:", self.supplier_name_input)
        form_layout.addRow("Contacto:", self.supplier_contact_input)
        form_layout.addRow("Teléfono:", self.supplier_phone_input)
        form_layout.addRow("Email:", self.supplier_email_input)

        left_layout.addWidget(form_widget)

        # Espacio entre el formulario y los botones
        left_layout.addSpacing(10)

        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Espaciado entre botones

        self.add_supplier_button = QPushButton("Agregar proveedor")
        self.add_supplier_button.setIcon(QIcon("icons/add.png"))
        self.add_supplier_button.clicked.connect(self.add_supplier)

        self.clear_form_button = QPushButton("Limpiar formulario")
        self.clear_form_button.setIcon(QIcon("icons/clear.png"))
        self.clear_form_button.clicked.connect(self.clear_form)

        button_layout.addWidget(self.add_supplier_button)
        button_layout.addWidget(self.clear_form_button)

        left_layout.addLayout(button_layout)

        # Espacio adicional antes del frame de estadísticas
        left_layout.addSpacing(20)

        # Estadísticas de proveedores
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_frame.setStyleSheet("background-color: #2C3E50; padding: 10px; border-radius: 5px;")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(5)

        self.total_suppliers_label = QLabel("Total de proveedores: 0")
        self.total_suppliers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_suppliers_label.setFont(QFont("Segoe UI", 12))
        self.total_suppliers_label.setStyleSheet("color: #ECF0F1;")
        stats_layout.addWidget(self.total_suppliers_label)

        left_layout.addWidget(stats_frame)

        # Espacio adicional para empujar los elementos hacia arriba
        left_layout.addStretch(1)

        # Panel derecho
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar proveedores...")
        self.search_input.textChanged.connect(self.search_suppliers)
        search_layout.addWidget(self.search_input)

        right_layout.addLayout(search_layout)

        # Tabla de proveedores
        self.supplier_table = QTableWidget(0, 5)
        self.supplier_table.setHorizontalHeaderLabels(["ID", "Nombre", "Contacto", "Teléfono", "Email"])
        
        # Deshabilitar edición directa
        self.supplier_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Mejorar los encabezados
        self.supplier_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.supplier_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #4CAF50;  /* Fondo de los encabezados */
                color: white;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ddd;
            }
        """)
        
        # Alternar colores de las filas y otros estilos visuales
        self.supplier_table.setAlternatingRowColors(True)
        self.supplier_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #BFBFBF;
                background-color: #f9f9f9;  /* Color de fondo de la tabla */
                alternate-background-color: #F2F2F2;  /* Color de fondo alternado */
            }
            QTableWidget::item {
                padding: 8px;  /* Mejorar el espaciado en las celdas */
                border-bottom: 1px solid #ddd;
            }
            QTableWidget::item:selected {
                background-color: #3399FF;  /* Color de selección */
                color: white;
            }
        """)

        right_layout.addWidget(self.supplier_table)

        # Botones de acción para la tabla
        table_button_layout = QHBoxLayout()
        table_button_layout.setSpacing(10)  # Espaciado entre los botones de la tabla

        self.edit_supplier_button = QPushButton("Editar proveedor")
        self.edit_supplier_button.setIcon(QIcon("icons/edit.png"))
        self.edit_supplier_button.clicked.connect(self.edit_supplier)

        self.delete_supplier_button = QPushButton("Eliminar proveedor")
        self.delete_supplier_button.setIcon(QIcon("icons/delete.png"))
        self.delete_supplier_button.clicked.connect(self.delete_supplier)

        table_button_layout.addWidget(self.edit_supplier_button)
        table_button_layout.addWidget(self.delete_supplier_button)

        right_layout.addLayout(table_button_layout)

        # Agregar paneles al diseño principal usando QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Ajustar tamaños iniciales de los paneles
        splitter.setSizes([300, 500])  # Panel izquierdo 300px, derecho 500px

        main_layout.addWidget(splitter)
    def add_supplier(self):
        name = self.supplier_name_input.text()
        contact = self.supplier_contact_input.text()
        phone = self.supplier_phone_input.text()
        email = self.supplier_email_input.text()

        if not name:
            QMessageBox.critical(self, 'Error', "Por favor, ingrese un nombre de proveedor.")
            return

        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("INSERT INTO proveedores (nombre, contacto, telefono, email) VALUES (?, ?, ?, ?)",
                      (name, contact, phone, email))
            conn.commit()
            conn.close()

            self.clear_form()
            self.load_suppliers()
            self.supplier_updated.emit()

            QMessageBox.information(self, 'Éxito', "Proveedor agregado correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Error', f"No se pudo agregar el proveedor: {e}")

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

            self.total_suppliers_label.setText(f"Total de proveedores: {len(suppliers)}")

        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Error', f"No se pudieron cargar los proveedores: {e}")

    def edit_supplier(self):
        selected_items = self.supplier_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Advertencia', "Por favor, seleccione un proveedor para editar.")
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

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

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
                QMessageBox.information(self, 'Éxito', "Proveedor actualizado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, 'Error', f"No se pudo actualizar el proveedor: {e}")

    def delete_supplier(self):
        selected_items = self.supplier_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Advertencia', "Por favor, seleccione un proveedor para eliminar.")
            return

        row = selected_items[0].row()
        supplier_id = int(self.supplier_table.item(row, 0).text())

        reply = QMessageBox.question(self, 'Confirmación', "¿Está seguro de que desea eliminar este proveedor?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('pos_database.db')
                c = conn.cursor()
                c.execute("DELETE FROM proveedores WHERE id = ?", (supplier_id,))
                conn.commit()
                conn.close()

                self.load_suppliers()
                QMessageBox.information(self, 'Éxito', "Proveedor eliminado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, 'Error', f"No se pudo eliminar el proveedor: {e}")

    def clear_form(self):
        self.supplier_name_input.clear()
        self.supplier_contact_input.clear()
        self.supplier_phone_input.clear()
        self.supplier_email_input.clear()

    def search_suppliers(self, query):
        for row in range(self.supplier_table.rowCount()):
            supplier_name = self.supplier_table.item(row, 1).text().lower()
            if query.lower() in supplier_name:
                self.supplier_table.setRowHidden(row, False)
            else:
                self.supplier_table.setRowHidden(row, True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SuppliersModule()
    window.show()
    sys.exit(app.exec())