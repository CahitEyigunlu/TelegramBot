import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file="tracker.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        """Veritabanında gerekli tabloları oluşturur."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phone_status (
                phone_number TEXT PRIMARY KEY,
                last_status TEXT,
                last_checked TIMESTAMP,
                last_seen TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP
            );
        """)
        self.conn.commit()

    def get_last_status(self, phone_number):
        """Telefon numarasının son durumunu getirir."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT last_status, last_checked, last_seen FROM phone_status WHERE phone_number = ?", (phone_number,))
        return cursor.fetchone()

    def update_status(self, phone_number, new_status, last_seen=None):
        """Telefon numarasının durumunu günceller."""
        cursor = self.conn.cursor()
        now = datetime.now()

        cursor.execute("""
            INSERT INTO phone_status (phone_number, last_status, last_checked, last_seen)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(phone_number)
            DO UPDATE SET last_status=excluded.last_status, last_checked=excluded.last_checked, last_seen=excluded.last_seen
            WHERE excluded.last_status != last_status OR excluded.last_seen != last_seen;
        """, (phone_number, new_status, now, last_seen))
        self.conn.commit()

    def log_status_change(self, phone_number, new_status, start_time, end_time=None):
        """Durum değişikliğini loglar."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO status_log (phone_number, status, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """, (phone_number, new_status, start_time, end_time))
        self.conn.commit()

    def close(self):
        """Veritabanı bağlantısını kapatır."""
        self.conn.close()
