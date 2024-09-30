from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox, QApplication, QComboBox, QStackedWidget,
    QSplitter, QFrame
)
from PyQt6.QtGui import QFont, QColor, QIcon, QPalette
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import sqlite3
import sys

class CustomersModule(QWidget):
    customer_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_customers()

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
                background-color: #4CAF50;
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
                background-color: #45a049;
            }
            QLineEdit {
                padding: 10px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: 1px solid #ddd;
            }
            QLabel {
                font-size: 14px;
            }
        """)

        # Panel izquierdo
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Título
        title = QLabel("Gestión de Clientes")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50; margin: 20px 0;")
        left_layout.addWidget(title)

        # Formulario de entrada
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Nombre del cliente")
        self.customer_email_input = QLineEdit()
        self.customer_email_input.setPlaceholderText("Email")
        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setPlaceholderText("Teléfono")
        
        form_layout.addRow("Nombre:", self.customer_name_input)
        form_layout.addRow("Email:", self.customer_email_input)
        form_layout.addRow("Teléfono:", self.customer_phone_input)

        left_layout.addWidget(form_widget)

        # Botones de acción
        button_layout = QHBoxLayout()
        self.add_customer_button = QPushButton("Agregar cliente")
        self.add_customer_button.setIcon(QIcon("icons/add.png"))
        self.add_customer_button.clicked.connect(self.add_customer)
        self.clear_form_button = QPushButton("Limpiar formulario")
        self.clear_form_button.setIcon(QIcon("icons/clear.png"))
        self.clear_form_button.clicked.connect(self.clear_form)

        button_layout.addWidget(self.add_customer_button)
        button_layout.addWidget(self.clear_form_button)

        left_layout.addLayout(button_layout)

        # Estadísticas de clientes
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_frame.setStyleSheet("background-color: white; padding: 10px; border-radius: 5px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        self.total_customers_label = QLabel("Total de clientes: 0")
        self.total_customers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_customers_label.setFont(QFont("Segoe UI", 16))
        stats_layout.addWidget(self.total_customers_label)

        left_layout.addWidget(stats_frame)

        left_layout.addStretch(1)

        # Panel derecho
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar clientes...")
        self.search_input.textChanged.connect(self.search_customers)
        search_layout.addWidget(self.search_input)

        right_layout.addLayout(search_layout)

        # Tabla de clientes
        self.customer_table = QTableWidget(0, 4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Teléfono"])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d6d9dc;
                selection-background-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.customer_table)

        # Botones de acción para la tabla
        table_button_layout = QHBoxLayout()
        self.edit_customer_button = QPushButton("Editar cliente")
        self.edit_customer_button.setIcon(QIcon("icons/edit.png"))
        self.edit_customer_button.clicked.connect(self.edit_customer)
        self.delete_customer_button = QPushButton("Eliminar cliente")
        self.delete_customer_button.setIcon(QIcon("icons/delete.png"))
        self.delete_customer_button.clicked.connect(self.delete_customer)

        table_button_layout.addWidget(self.edit_customer_button)
        table_button_layout.addWidget(self.delete_customer_button)

        right_layout.addLayout(table_button_layout)

        # Agregar paneles al diseño principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([int(self.width() * 0.4), int(self.width() * 0.6)])

        main_layout.addWidget(splitter)

    def add_customer(self):
        name = self.customer_name_input.text()
        email = self.customer_email_input.text()
        phone = self.customer_phone_input.text()

        if not name:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nombre de cliente.")
            return

        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("INSERT INTO clientes (nombre, email, telefono) VALUES (?, ?, ?)", (name, email, phone))
            conn.commit()
            conn.close()

            self.clear_form()
            self.load_customers()
            self.customer_updated.emit()

            QMessageBox.information(self, "Éxito", "Cliente agregado correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el cliente: {e}")

    def load_customers(self):
        try:
            conn = sqlite3.connect('pos_database.db')
            c = conn.cursor()
            c.execute("SELECT * FROM clientes")
            customers = c.fetchall()
            conn.close()

            self.customer_table.setRowCount(0)
            for row, customer in enumerate(customers):
                self.customer_table.insertRow(row)
                for col, value in enumerate(customer):
                    item = QTableWidgetItem(str(value))
                    if col == 0:  # ID column
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.customer_table.setItem(row, col, item)

            self.total_customers_label.setText(f"Total de clientes: {len(customers)}")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los clientes: {e}")

    def edit_customer(self):
        selected_items = self.customer_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un cliente para editar.")
            return

        row = selected_items[0].row()
        customer_id = int(self.customer_table.item(row, 0).text())
        current_name = self.customer_table.item(row, 1).text()
        current_email = self.customer_table.item(row, 2).text()
        current_phone = self.customer_table.item(row, 3).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Cliente")
        layout = QFormLayout(dialog)

        name_input = QLineEdit(current_name)
        email_input = QLineEdit(current_email)
        phone_input = QLineEdit(current_phone)

        layout.addRow("Nombre:", name_input)
        layout.addRow("Email:", email_input)
        layout.addRow("Teléfono:", phone_input)

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
            new_email = email_input.text()
            new_phone = phone_input.text()

            try:
                conn = sqlite3.connect('pos_database.db')
                c = conn.cursor()
                c.execute("""
                    UPDATE clientes
                    SET nombre = ?, email = ?, telefono = ?
                    WHERE id = ?
                """, (new_name, new_email, new_phone, customer_id))
                conn.commit()
                conn.close()

                self.load_customers()
                self.customer_updated.emit()
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el cliente: {e}")

    def delete_customer(self):
        selected_items = self.customer_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un cliente para eliminar.")
            return

        row = selected_items[0].row()
        customer_id = int(self.customer_table.item(row, 0).text())
        customer_name = self.customer_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirmar eliminación",
                                     f"¿Está seguro de que desea eliminar el cliente '{customer_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('pos_database.db')
                c = conn.cursor()
                c.execute("DELETE FROM clientes WHERE id = ?", (customer_id,))
                conn.commit()
                conn.close()

                self.load_customers()
                self.customer_updated.emit()
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el cliente: {e}")

    def clear_form(self):
        self.customer_name_input.clear()
        self.customer_email_input.clear()
        self.customer_phone_input.clear()

    def search_customers(self):
        search_text = self.search_input.text().lower()
        for row in range(self.customer_table.rowCount()):
            match = False
            for col in range(1, self.customer_table.columnCount()):  # Excluye la columna ID
                item = self.customer_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.customer_table.setRowHidden(row, not match)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    customers_module = CustomersModule()
    customers_module.show()
    sys.exit(app.exec())