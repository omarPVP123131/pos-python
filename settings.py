from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
import sqlite3
import os

class SettingsModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.backup_button = QPushButton("Realizar copia de seguridad")
        self.restore_button = QPushButton("Restaurar copia de seguridad")

        layout.addWidget(self.backup_button)
        layout.addWidget(self.restore_button)

        self.setLayout(layout)

        self.backup_button.clicked.connect(self.backup_database)
        self.restore_button.clicked.connect(self.restore_database)

    def backup_database(self):
        backup_path, _ = QFileDialog.getSaveFileName(self, "Guardar copia de seguridad", "", "SQLite DB Files (*.db)")
        if backup_path:
            conn = sqlite3.connect('pos_database.db')
            backup = sqlite3.connect(backup_path)
            conn.backup(backup)
            backup.close()
            conn.close()
            QLabel("Copia de seguridad realizada con éxito").show()

    def restore_database(self):
        restore_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar copia de seguridad", "", "SQLite DB Files (*.db)")
        if restore_path:
            conn = sqlite3.connect('pos_database.db')
            backup = sqlite3.connect(restore_path)
            backup.backup(conn)
            conn.close()
            backup.close()
            QLabel("Base de datos restaurada con éxito").show()