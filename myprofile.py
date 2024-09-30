from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QTextEdit, QListWidget, QFrame, QGridLayout, QScrollArea, QSizePolicy,
    QSpacerItem, QMessageBox, QDialog, QFormLayout, QCalendarWidget, QTabWidget,
    QFileDialog, QProgressBar, QGroupBox, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap
import sqlite3
from datetime import datetime, timedelta
import os
import shutil

class ProfileModule(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_user_data()
        self.start_session_timer()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QGroupBox {
                border: 2px solid #34495e;
                border-radius: 5px;
                margin-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)

        # User info
        self.user_info_widget = self.create_user_info_widget()
        left_layout.addWidget(self.user_info_widget)

        # Action buttons
        self.create_action_buttons(left_layout)

        left_layout.addStretch(1)
        main_layout.addWidget(left_panel, 1)

        # Right panel
        right_panel = QTabWidget()
        right_panel.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3498db;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 10px 15px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)

        # User stats tab
        stats_tab = self.create_user_stats_tab()
        right_panel.addTab(stats_tab, "Estadísticas")

        # Session history tab
        history_tab = self.create_session_history_tab()
        right_panel.addTab(history_tab, "Historial de Sesiones")

        # Calendar tab
        calendar_tab = self.create_calendar_tab()
        right_panel.addTab(calendar_tab, "Calendario")

        # Notes tab
        notes_tab = self.create_notes_tab()
        right_panel.addTab(notes_tab, "Notas")

        # Añadir nueva pestaña de objetivos
        goals_tab = self.create_goals_tab()
        right_panel.addTab(goals_tab, "Objetivos")
        main_layout.addWidget(right_panel, 2)

    def create_user_info_widget(self):
        user_info_group = QGroupBox("Información del Usuario")
        user_info_layout = QVBoxLayout(user_info_group)

        self.profile_picture = QLabel()
        self.profile_picture.setFixedSize(100, 100)
        self.profile_picture.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                border-radius: 50px;
            }
        """)
        self.profile_picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(self.profile_picture, alignment=Qt.AlignmentFlag.AlignCenter)

        change_picture_button = QPushButton("Cambiar foto")
        change_picture_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        change_picture_button.clicked.connect(self.change_profile_picture)
        user_info_layout.addWidget(change_picture_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.username_label = QLabel()
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        user_info_layout.addWidget(self.username_label)

        self.role_label = QLabel()
        self.role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(self.role_label)

        self.email_label = QLabel()
        self.email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(self.email_label)

        self.session_time_label = QLabel()
        self.session_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(self.session_time_label)

        return user_info_group

    def create_goals_tab(self):
            goals_widget = QWidget()
            goals_layout = QVBoxLayout(goals_widget)

            self.goals_list = QListWidget()
            self.goals_list.setStyleSheet("""
                QListWidget {
                    background-color: #ecf0f1;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                }
                QListWidget::item {
                    background-color: white;
                    color: #2c3e50;
                    border-radius: 3px;
                    padding: 5px;
                    margin-bottom: 5px;
                }
                QListWidget::item:hover {
                    background-color: #bdc3c7;
                }
            """)
            goals_layout.addWidget(self.goals_list)

            add_goal_button = QPushButton("Añadir Objetivo")
            add_goal_button.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            add_goal_button.clicked.connect(self.add_goal)
            goals_layout.addWidget(add_goal_button)

            complete_goal_button = QPushButton("Marcar como Completado")
            complete_goal_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            complete_goal_button.clicked.connect(self.complete_goal)
            goals_layout.addWidget(complete_goal_button)

            return goals_widget

    def load_user_data(self):
        # ... (el resto del método load_user_data permanece igual)

        # Cargar objetivos del usuario
        self.load_goals()

    def load_goals(self):
        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            c.execute("SELECT id, goal, target_date, completed FROM user_goals WHERE user_id = ?", (self.user_id,))
            goals = c.fetchall()
            
            self.goals_list.clear()
            for goal_id, goal, target_date, completed in goals:
                status = "Completado" if completed else "Pendiente"
                self.goals_list.addItem(f"{goal} - Fecha objetivo: {target_date} - Estado: {status}")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al cargar los objetivos: {str(e)}")
        finally:
            if conn:
                conn.close()

    def add_goal(self):
        goal, ok = QInputDialog.getText(self, "Añadir Objetivo", "Ingrese su nuevo objetivo:")
        if ok and goal:
            target_date, ok = QInputDialog.getText(self, "Fecha Objetivo", "Ingrese la fecha objetivo (YYYY-MM-DD):")
            if ok and target_date:
                try:
                    conn = sqlite3.connect("pos_database.db")
                    c = conn.cursor()
                    
                    c.execute("INSERT INTO user_goals (user_id, goal, target_date) VALUES (?, ?, ?)",
                              (self.user_id, goal, target_date))
                    conn.commit()
                    
                    QMessageBox.information(self, "Éxito", "Objetivo añadido correctamente.")
                    self.load_goals()
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Error de Base de Datos", f"Error al añadir el objetivo: {str(e)}")
                finally:
                    if conn:
                        conn.close()

    def complete_goal(self):
        current_item = self.goals_list.currentItem()
        if current_item:
            goal_text = current_item.text().split(" - ")[0]
            try:
                conn = sqlite3.connect("pos_database.db")
                c = conn.cursor()
                
                c.execute("UPDATE user_goals SET completed = 1 WHERE user_id = ? AND goal = ?",
                          (self.user_id, goal_text))
                conn.commit()
                
                QMessageBox.information(self, "Éxito", "Objetivo marcado como completado.")
                self.load_goals()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"Error al completar el objetivo: {str(e)}")
            finally:
                if conn:
                    conn.close()
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un objetivo para marcar como completado.")

    # Nuevo método para exportar datos del usuario
    def export_user_data(self):
        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            c.execute("SELECT * FROM usuarios WHERE id = ?", (self.user_id,))
            user_data = c.fetchone()
            
            c.execute("SELECT * FROM user_notes WHERE user_id = ?", (self.user_id,))
            notes = c.fetchone()
            
            c.execute("SELECT * FROM user_goals WHERE user_id = ?", (self.user_id,))
            goals = c.fetchall()
            
            export_data = f"Datos del Usuario:\n{user_data}\n\nNotas:\n{notes}\n\nObjetivos:\n"
            for goal in goals:
                export_data += f"{goal}\n"
            
            file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Datos", "", "Archivo de Texto (*.txt)")
            if file_name:
                with open(file_name, 'w') as file:
                    file.write(export_data)
                QMessageBox.information(self, "Éxito", "Datos exportados correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al exportar los datos: {str(e)}")
        finally:
            if conn:
                conn.close()
                
    def create_action_buttons(self, layout):
        action_group = QGroupBox("Acciones")
        action_layout = QVBoxLayout(action_group)

        edit_profile_button = self.create_button("Editar Perfil", "edit_icon.png")
        edit_profile_button.clicked.connect(self.edit_profile)
        action_layout.addWidget(edit_profile_button)

        change_password_button = self.create_button("Cambiar Contraseña", "password_icon.png")
        change_password_button.clicked.connect(self.change_password)
        action_layout.addWidget(change_password_button)

        logout_button = self.create_button("Cerrar Sesión", "logout_icon.png")
        logout_button.clicked.connect(self.logout)
        action_layout.addWidget(logout_button)

        export_data_button = self.create_button("Exportar Datos", "export_icon.png")
        export_data_button.clicked.connect(self.export_user_data)
        action_layout.addWidget(export_data_button)
        
        layout.addWidget(action_group)

    def create_button(self, text, icon_path):
        button = QPushButton(text)
        button.setIcon(QIcon(icon_path))
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                text-align: left;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        return button

    def create_user_stats_tab(self):
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)

        stats_scroll = QScrollArea()
        stats_scroll.setWidgetResizable(True)
        stats_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)

        stats_content = QWidget()
        stats_content_layout = QVBoxLayout(stats_content)

        # Total sales
        self.total_sales_label = QLabel("Ventas totales: $0")
        stats_content_layout.addWidget(self.total_sales_label)

        # Total logins
        self.total_logins_label = QLabel("Inicios de sesión totales: 0")
        stats_content_layout.addWidget(self.total_logins_label)

        # Average session time
        self.avg_session_time_label = QLabel("Tiempo promedio de sesión: 0:00:00")
        stats_content_layout.addWidget(self.avg_session_time_label)

        # Last login
        self.last_login_label = QLabel("Último inicio de sesión: N/A")
        stats_content_layout.addWidget(self.last_login_label)

        # Account creation date
        self.account_creation_label = QLabel("Fecha de creación de cuenta: N/A")
        stats_content_layout.addWidget(self.account_creation_label)

        stats_content_layout.addStretch(1)
        stats_scroll.setWidget(stats_content)
        stats_layout.addWidget(stats_scroll)

        return stats_widget

    def create_session_history_tab(self):
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                background-color: #ecf0f1;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                background-color: white;
                color: #2c3e50;
                border-radius: 3px;
                padding: 5px;
                margin-bottom: 5px;
            }
            QListWidget::item:hover {
                background-color: #bdc3c7;
            }
        """)
        history_layout.addWidget(self.session_list)

        return history_widget

    def create_calendar_tab(self):
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)

        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget QToolButton {
                color: white;
                background-color: #3498db;
            }
            QCalendarWidget QMenu {
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                color: #2c3e50;
                background-color: #ecf0f1;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #2c3e50;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        calendar_layout.addWidget(self.calendar)

        self.calendar.selectionChanged.connect(self.on_date_selected)

        self.date_events_list = QListWidget()
        self.date_events_list.setStyleSheet("""
            QListWidget {
                background-color: #ecf0f1;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                background-color: white;
                color: #2c3e50;
                border-radius: 3px;
                padding: 5px;
                margin-bottom: 5px;
            }
        """)
        calendar_layout.addWidget(self.date_events_list)

        return calendar_widget

    def create_notes_tab(self):
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)

        self.notes_text = QTextEdit()
        self.notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #ecf0f1;
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: #2c3e50;
            }
        """)
        notes_layout.addWidget(self.notes_text)

        save_notes_button = QPushButton("Guardar Notas")
        save_notes_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_notes_button.clicked.connect(self.save_notes)
        notes_layout.addWidget(save_notes_button)

        return notes_widget

    def load_user_data(self):
        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            # Verificar si la columna user_id existe en la tabla ventas
            c.execute("PRAGMA table_info(ventas)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'user_id' not in columns:
                QMessageBox.warning(self, "Advertencia", "La columna 'user_id' no existe en la tabla 'ventas'. Algunas estadísticas pueden no estar disponibles.")
            
            c.execute("SELECT username, role, email, profile_picture, created_at FROM usuarios WHERE id = ?", (self.user_id,))
            user_data = c.fetchone()
            
            if user_data:
                self.username_label.setText(user_data[0])
                self.role_label.setText(f"Rol: {user_data[1]}")
                self.email_label.setText(user_data[2])
                
                if user_data[3]:
                    self.load_profile_picture(user_data[3])
                else:
                    self.profile_picture.setText("Sin foto")
                    self.profile_picture.setStyleSheet("""
                        QLabel {
                            background-color: #34495e;
                            color: #ecf0f1;
                            border-radius: 50px;
                            font-size: 14px;
                        }
                    """)
                
                if user_data[4]:
                    self.account_creation_label.setText(f"Fecha de creación de cuenta: {user_data[4]}")
                else:
                    self.account_creation_label.setText("Fecha de creación de cuenta: No disponible")

            # Cargar historial de sesiones
            c.execute("SELECT login_time, logout_time FROM usuarios WHERE id = ? ORDER BY login_time DESC LIMIT 10", (self.user_id,))
            sessions = c.fetchall()

            self.session_list.clear()
            for login, logout in sessions:
                if logout:
                    self.session_list.addItem(f"Inicio: {login} - Cierre: {logout}")
                else:
                    self.session_list.addItem(f"Inicio: {login} - Sesión actual")

            # Cargar estadísticas del usuario
            if 'user_id' in columns:
                c.execute("SELECT SUM(total) FROM ventas WHERE user_id = ?", (self.user_id,))
                total_sales = c.fetchone()[0] or 0
                self.total_sales_label.setText(f"Ventas totales: ${total_sales:.2f}")
            else:
                self.total_sales_label.setText("Ventas totales: No disponible")

            c.execute("SELECT COUNT(*) FROM usuarios WHERE id = ?", (self.user_id,))
            total_logins = c.fetchone()[0] or 0
            self.total_logins_label.setText(f"Inicios de sesión totales: {total_logins}")

            c.execute("SELECT AVG(JULIANDAY(logout_time) - JULIANDAY(login_time)) * 24 * 60 * 60 FROM usuarios WHERE id = ? AND logout_time IS NOT NULL", (self.user_id,))
            avg_session_time = c.fetchone()[0] or 0
            avg_session_time = timedelta(seconds=int(avg_session_time))
            self.avg_session_time_label.setText(f"Tiempo promedio de sesión: {avg_session_time}")

            c.execute("SELECT login_time FROM usuarios WHERE id = ? ORDER BY login_time DESC LIMIT 1", (self.user_id,))
            last_login = c.fetchone()
            if last_login:
                self.last_login_label.setText(f"Último inicio de sesión: {last_login[0]}")
            else:
                self.last_login_label.setText("Último inicio de sesión: No disponible")

            # Cargar notas del usuario
            c.execute("SELECT notes FROM user_notes WHERE user_id = ?", (self.user_id,))
            notes = c.fetchone()
            if notes:
                self.notes_text.setPlainText(notes[0])
            else:
                self.notes_text.clear()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al cargar los datos del usuario: {str(e)}")
        finally:
            if conn:
                conn.close()
    def start_session_timer(self):
        self.session_start = datetime.now()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_session_time)
        self.timer.start(1000)

    def update_session_time(self):
        current_time = datetime.now()
        elapsed_time = current_time - self.session_start
        hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.session_time_label.setText(f"Tiempo de sesión: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def edit_profile(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Perfil")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
        """)
        layout = QFormLayout(dialog)

        username_input = QLineEdit(self.username_label.text())
        email_input = QLineEdit(self.email_label.text())

        layout.addRow("Usuario:", username_input)
        layout.addRow("Email:", email_input)

        buttons = QHBoxLayout()
        save_button = QPushButton("Guardar")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)

        save_button.clicked.connect(lambda: self.save_profile(username_input.text(), email_input.text(), dialog))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

    def save_profile(self, username, email, dialog):
        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            c.execute("UPDATE usuarios SET username = ?, email = ? WHERE id = ?", (username, email, self.user_id))
            conn.commit()

            self.username_label.setText(username)
            self.email_label.setText(email)
            
            dialog.accept()
            QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar el perfil: {str(e)}")
        finally:
            if conn:
                conn.close()

    def change_password(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar Contraseña")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
        """)
        layout = QFormLayout(dialog)

        current_password = QLineEdit()
        current_password.setEchoMode(QLineEdit.EchoMode.Password)
        new_password = QLineEdit()
        new_password.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_password = QLineEdit()
        confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Contraseña actual:", current_password)
        layout.addRow("Nueva contraseña:", new_password)
        layout.addRow("Confirmar contraseña:", confirm_password)

        buttons = QHBoxLayout()
        save_button = QPushButton("Guardar")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)

        save_button.clicked.connect(lambda: self.save_password(current_password.text(), new_password.text(), confirm_password.text(), dialog))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

    def save_password(self, current_password, new_password, confirm_password, dialog):
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Las nuevas contraseñas no coinciden.")
            return

        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            c.execute("SELECT password FROM usuarios WHERE id = ?", (self.user_id,))
            stored_password = c.fetchone()[0]

            if current_password != stored_password:
                QMessageBox.warning(self, "Error", "La contraseña actual es incorrecta.")
                return

            c.execute("UPDATE usuarios SET password = ? WHERE id = ?", (new_password, self.user_id))
            conn.commit()

            dialog.accept()
            QMessageBox.information(self, "Éxito", "Contraseña actualizada correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar la contraseña: {str(e)}")
        finally:
            if conn:
                conn.close()

    def logout(self):
        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE usuarios SET logout_time = ? WHERE id = ?", (logout_time, self.user_id))
            
            conn.commit()
            self.logout_signal.emit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al cerrar sesión: {str(e)}")
        finally:
            if conn:
                conn.close()

    def change_profile_picture(self):
        file_dialog = QFileDialog()
        image_file, _ = file_dialog.getOpenFileName(self, "Seleccionar imagen de perfil", "", "Imágenes (*.png *.jpg *.bmp)")
        
        if image_file:
            try:
                # Crear directorio para imágenes de perfil si no existe
                profile_pictures_dir = "profile_pictures"
                os.makedirs(profile_pictures_dir, exist_ok=True)
                
                # Generar un nombre único para la imagen
                _, ext = os.path.splitext(image_file)
                new_filename = f"user_{self.user_id}_profile{ext}"
                destination = os.path.join(profile_pictures_dir, new_filename)
                
                # Copiar la imagen al directorio de imágenes de perfil
                shutil.copy(image_file, destination)
                
                # Actualizar la base de datos con la ruta relativa de la imagen
                conn = sqlite3.connect("pos_database.db")
                c = conn.cursor()
                
                c.execute("UPDATE usuarios SET profile_picture = ? WHERE id = ?", (destination, self.user_id))
                conn.commit()
                
                # Cargar la nueva imagen de perfil
                self.load_profile_picture(destination)
                
                QMessageBox.information(self, "Éxito", "Imagen de perfil actualizada correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar la imagen de perfil: {str(e)}")
            finally:
                if conn:
                    conn.close()

    def load_profile_picture(self, picture_path):
        if picture_path and os.path.exists(picture_path):
            pixmap = QPixmap(picture_path)
            self.profile_picture.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.profile_picture.setText("Sin foto")
            self.profile_picture.setStyleSheet("""
                QLabel {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border-radius: 50px;
                    font-size: 14px;
                }
            """)

    def on_date_selected(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        
        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            c.execute("SELECT login_time, logout_time FROM usuarios WHERE id = ? AND DATE(login_time) = ?", (self.user_id, selected_date))
            sessions = c.fetchall()
            
            self.date_events_list.clear()
            for login, logout in sessions:
                if logout:
                    self.date_events_list.addItem(f"Sesión: {login} - {logout}")
                else:
                    self.date_events_list.addItem(f"Sesión iniciada: {login}")
            
            c.execute("SELECT fecha, total FROM ventas WHERE user_id = ? AND DATE(fecha) = ?", (self.user_id, selected_date))
            sales = c.fetchall()
            
            for date, total in sales:
                self.date_events_list.addItem(f"Venta: {date} - ${total:.2f}")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al cargar eventos del día: {str(e)}")
        finally:
            if conn:
                conn.close()

    def save_notes(self):
        notes = self.notes_text.toPlainText()
        
        try:
            conn = sqlite3.connect("pos_database.db")
            c = conn.cursor()
            
            c.execute("INSERT OR REPLACE INTO user_notes (user_id, notes) VALUES (?, ?)", (self.user_id, notes))
            conn.commit()
            
            QMessageBox.information(self, "Éxito", "Notas guardadas correctamente.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al guardar las notas: {str(e)}")
        finally:
            if conn:
                conn.close()