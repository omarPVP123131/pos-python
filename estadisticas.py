from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QDate
import sqlite3

class StatisticsModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.generate_report_button = QPushButton("Generar reporte")
        self.report_table = QTableWidget(0, 3)
        self.report_table.setHorizontalHeaderLabels(["Fecha", "Tipo", "Valor"])

        layout.addWidget(QLabel("Fecha de inicio:"))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel("Fecha de fin:"))
        layout.addWidget(self.end_date)
        layout.addWidget(self.generate_report_button)
        layout.addWidget(self.report_table)

        self.setLayout(layout)

        self.generate_report_button.clicked.connect(self.generate_report)

    def generate_report(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("SELECT fecha, tipo, valor FROM estadisticas WHERE fecha BETWEEN ? AND ?", (start, end))
        stats = c.fetchall()
        conn.close()

        self.report_table.setRowCount(0)
        for row, stat in enumerate(stats):
            self.report_table.insertRow(row)
            for col, value in enumerate(stat):
                self.report_table.setItem(row, col, QTableWidgetItem(str(value)))