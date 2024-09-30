from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget
import sqlite3
from datetime import datetime

class NotesModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.note_title_input = QLineEdit()
        self.note_content_input = QTextEdit()
        self.add_note_button = QPushButton("Agregar nota")
        self.notes_list = QListWidget()

        layout.addWidget(QLabel("Título de la nota:"))
        layout.addWidget(self.note_title_input)
        layout.addWidget(QLabel("Contenido:"))
        layout.addWidget(self.note_content_input)
        layout.addWidget(self.add_note_button)
        layout.addWidget(self.notes_list)

        self.setLayout(layout)

        self.add_note_button.clicked.connect(self.add_note)
        self.load_notes()

    def add_note(self):
        title = self.note_title_input.text()
        content = self.note_content_input.toPlainText()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("INSERT INTO notas (titulo, contenido, fecha) VALUES (?, ?, ?)", (title, content, date))
        conn.commit()
        conn.close()

        self.load_notes()

    def load_notes(self):
        conn = sqlite3.connect('pos_database.db')
        c = conn.cursor()
        c.execute("SELECT titulo, fecha FROM notas ORDER BY fecha DESC")
        notes = c.fetchall()
        conn.close()

        self.notes_list.clear()
        for note in notes:
            self.notes_list.addItem(f"{note[0]} - {note[1]}")