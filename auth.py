import sqlite3
from PyQt6.QtCore import QObject, pyqtSignal

class AuthManager(QObject):
    login_success = pyqtSignal(int)
    login_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def attempt_login(self, username, password):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()
        c.execute(
            "SELECT id FROM usuarios WHERE username=? AND password=?",
            (username, password),
        )
        user = c.fetchone()
        conn.close()

        if user:
            user_id = user[0]
            self.log_session(user_id, True)
            self.login_success.emit(user_id)
        else:
            self.login_failed.emit("Incorrect username or password")

    def log_session(self, user_id, is_login):
        conn = sqlite3.connect("pos_database.db")
        c = conn.cursor()
        if is_login:
            c.execute(
                "UPDATE usuarios SET login_time = datetime('now') WHERE id = ?",
                (user_id,),
            )
        else:
            c.execute(
                "UPDATE usuarios SET logout_time = datetime('now') WHERE id = ?",
                (user_id,),
            )
        conn.commit()
        conn.close()

    def logout(self, user_id):
        self.log_session(user_id, False)