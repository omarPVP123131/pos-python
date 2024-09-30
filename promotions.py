from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QDateEdit, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QDate
import sqlite3

class PromotionsModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.promo_name_input = QLineEdit()
        self.promo_description_input = QLineEdit()
        self.promo_start_date = QDateEdit()
        self.promo_end_date = QDateEdit()
        self.promo_discount_input = QLineEdit()
        self.add_promo_button = QPushButton("Agregar promoción")
        self.promo_table = QTableWidget(0, 5)
        self.promo_table.setHorizontalHeaderLabels(["Nombre", "Descripción", "Inicio", "Fin", "Descuento"])

        layout.addWidget(QLabel("Nombre de la promoción:"))
        layout.addWidget(self.promo_name_input)
        layout.addWidget(QLabel("Descripción:"))
        layout.addWidget(self.promo_description_input)
        layout.addWidget(QLabel("Fecha de inicio:"))
        layout.addWidget(self.promo_start_date)
        layout.addWidget(QLabel("Fecha de fin:"))
        layout.addWidget(self.promo_end_date)
        layout.addWidget(QLabel("Descuento (%):"))
        layout.addWidget(self.promo_discount_input)
        layout.addWidget(self.add_promo_button)
        layout.addWidget(self.promo_table)

        self.setLayout(layout)

        self.add_promo_button.clicked.connect(self.add_promotion)
        self.load_promotions()

    def add_promotion(self):
        name = self.promo_name_input.text()
        description = self.promo_description_input.text()
        start_date = self.promo_start_date.date().toString("yyyy-MM-dd")
        end_date = self.promo_end_date.date().toString("yyyy-MM-dd")
        discount = float(self.promo_discount_input.text())

        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("INSERT INTO promociones (nombre, descripcion, fecha_inicio, fecha_fin, descuento) VALUES (?, ?, ?, ?, ?)",
                  (name, description, start_date, end_date, discount))
        conn.commit()
        conn.close()

        self.load_promotions()

    def load_promotions(self):
        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("SELECT nombre, descripcion, fecha_inicio, fecha_fin, descuento FROM promociones")
        promotions = c.fetchall()
        conn.close()

        self.promo_table.setRowCount(0)
        for row, promo in enumerate(promotions):
            self.promo_table.insertRow(row)
            for col, value in enumerate(promo):
                self.promo_table.setItem(row, col, QTableWidgetItem(str(value)))