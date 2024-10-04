import sqlite3
import settings 
from datetime import datetime, timedelta
from termcolor import colored
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from error_handler import log_error
import asyncio
from session_manager import SessionManager

class TrackerDB:
    def __init__(self, db_file="tracker.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
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

    def update_status(self, phone_number, status, last_seen):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO phone_status (phone_number, last_status, last_checked, last_seen)
            VALUES (?, ?, ?, ?)
        """, (phone_number, status, datetime.now(), last_seen))
        self.conn.commit()

    def log_status_change(self, phone_number, status, start_time, end_time=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO status_log (phone_number, status, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """, (phone_number, status, start_time, end_time))
        self.conn.commit()

from telethon.tl.types import UserStatusOnline, UserStatusOffline
from datetime import datetime
from error_handler import log_error
from sqlite_db import SQLiteDB
from session_manager import SessionManager

class TrackerStatus:
    def __init__(self, db, session_manager, limit=5):
        self.db = db
        self.session_manager = session_manager
        self.limit = limit

    async def monitor_numbers(self, phone_numbers):
        for phone_number in phone_numbers:
            try:
                if not self.session_manager.is_connected():
                    await self.session_manager.start_session()

                # Telefon numarasının durumunu kontrol et
                client = self.session_manager.client  # client'e doğrudan erişiyoruz
                entity = await client.get_entity(phone_number)
                status = entity.status
                now = datetime.now()

                last_seen = None
                if isinstance(status, UserStatusOffline):
                    last_seen = status.was_online
                    current_status = "offline"
                elif isinstance(status, UserStatusOnline):
                    current_status = "online"
                else:
                    current_status = "unknown"

                # Durumları veritabanına kaydet
                self.db.update_status(phone_number, current_status, last_seen)
                self.db.log_status_change(phone_number, current_status, now)

            except Exception as e:
                log_error(f"{phone_number} için takip sırasında bir hata oluştu: {e}")
                raise e


async def main():
    db = TrackerDB()
    session_manager = SessionManager()
    tracker = TrackerStatus(db, session_manager, limit=5)
    phone_numbers = ["+905074510000", "+905432348436", "+905062739594"]  
    await tracker.monitor_numbers(phone_numbers)

if __name__ == "__main__":
    asyncio.run(main())
