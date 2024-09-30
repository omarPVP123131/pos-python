from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import sqlite3

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        
        if self.path == '/productos':
            c.execute("SELECT * FROM productos")
            productos = c.fetchall()
            self.wfile.write(json.dumps(productos).encode())
        elif self.path == '/ventas':
            c.execute("SELECT * FROM ventas")
            ventas = c.fetchall()
            self.wfile.write(json.dumps(ventas).encode())
        else:
            self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode())
        
        conn.close()

class LocalServerModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.start_button = QPushButton("Iniciar servidor")
        self.stop_button = QPushButton("Detener servidor")
        self.status_label = QLabel("Servidor detenido")

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)

        self.server = None
        self.server_thread = None

    def start_server(self):
        if not self.server:
            self.server = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.start()
            self.status_label.setText("Servidor en ejecución en http://localhost:8000")

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server_thread.join()
            self.server = None
            self.server_thread = None
            self.status_label.setText("Servidor detenido")