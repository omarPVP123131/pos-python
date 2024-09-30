from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem
import sqlite3

class LoyaltyModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.customer_id_input = QLineEdit()
        self.points_input = QLineEdit()
        self.add_points_button = QPushButton("Agregar puntos")
        self.redeem_points_button = QPushButton("Canjear puntos")
        self.loyalty_table = QTableWidget(0, 3)
        self.loyalty_table.setHorizontalHeaderLabels(["Cliente ID", "Nombre", "Puntos"])

        layout.addWidget(QLabel("ID del cliente:"))
        layout.addWidget(self.customer_id_input)
        layout.addWidget(QLabel("Puntos:"))
        layout.addWidget(self.points_input)
        layout.addWidget(self.add_points_button)
        layout.addWidget(self.redeem_points_button)
        layout.addWidget(self.loyalty_table)

        self.setLayout(layout)

        self.add_points_button.clicked.connect(self.add_points)
        self.redeem_points_button.clicked.connect(self.redeem_points)
        self.load_loyalty_data()

    def add_points(self):
        customer_id = int(self.customer_id_input.text())
        points = int(self.points_input.text())

        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO puntos (cliente_id, cantidad) VALUES (?, coalesce((SELECT cantidad FROM puntos WHERE cliente_id = ?) + ?, ?))",
                  (customer_id, customer_id, points, points))
        conn.commit()
        conn.close()

        self.load_loyalty_data()

    def redeem_points(self):
        customer_id = int(self.customer_id_input.text())
        points = int(self.points_input.text())

        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("UPDATE puntos SET cantidad = cantidad - ? WHERE cliente_id = ? AND cantidad >= ?",
                  (points, customer_id, points))
        conn.commit()
        conn.close()

        self.load_loyalty_data()

    def load_loyalty_data(self):
        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("SELECT c.id, c.nombre, COALESCE(p.cantidad, 0) FROM clientes c LEFT JOIN puntos p ON c.id = p.cliente_id")
        loyalty_data = c.fetchall()
        conn.close()

        self.loyalty_table.setRowCount(0)
        for row, data in enumerate(loyalty_data):
            self.loyalty_table.insertRow(row)
            for col, value in enumerate(data):
                self.loyalty_table.setItem(row, col, QTableWidgetItem(str(value)))