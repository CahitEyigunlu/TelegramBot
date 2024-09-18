import sqlite3
from datetime import datetime, timedelta
from termcolor import colored
from telethon.tl.types import UserStatusOnline, UserStatusOffline


class TrackerDB:
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


class StatusTracker:
    def __init__(self, db, client):
        self.db = db
        self.client = client

    async def check_phone_status(self, phone_number):
        """Telefon numarasının çevrimiçi durumunu kontrol eder."""
        try:
            # Numara için Telegram'da entity bulmaya çalışıyoruz
            entity = await self.client.get_entity(phone_number)
        except ValueError as e:
            # Eğer numara bulunamazsa, hata mesajı yazdırıyoruz
            print(colored(f"Cannot find any entity corresponding to {phone_number}.", "red"))
            return "not_found"
        except Exception as e:
            # Diğer beklenmedik hatalar için genel bir hata yönetimi
            print(colored(f"Bilinmeyen bir hata oluştu: {str(e)}", "red"))
            return "error"

        if entity.status is None:
            print(colored(f"{phone_number}'s status is hidden.", "yellow"))
            return "hidden"

        last_seen = None
        if isinstance(entity.status, UserStatusOnline):
            current_status = "online"
            print(colored(f"{phone_number} is online.", "green"))
        elif isinstance(entity.status, UserStatusOffline):
            current_status = "offline"
            last_seen = entity.status.was_online
            print(colored(f"{phone_number} was last seen at {last_seen}.", "red"))
        else:
            current_status = "unknown"

        self.track_status(phone_number, current_status, last_seen)
        return current_status






    def track_status(self, phone_number, current_status, last_seen=None):
        """Telefon numarasının durumunu kontrol eder ve gerekiyorsa günceller."""
        last_status = self.db.get_last_status(phone_number)
        now = datetime.now()

        if last_status:
            previous_status, last_checked_str, last_seen_db_str = last_status

            # Parse last_checked and last_seen dynamically based on their format
            last_checked = self.parse_datetime(last_checked_str)
            last_seen_db = self.parse_datetime(last_seen_db_str) if last_seen_db_str else None

            # Durum değişmişse güncelle
            if current_status != previous_status or last_seen != last_seen_db:
                if current_status == "online":
                    print(colored(f"{phone_number} is now online.", "green"))
                elif current_status == "offline":
                    print(colored(f"{phone_number} is now offline. Last seen: {last_seen}.", "red"))
                    if now - last_checked <= timedelta(seconds=10):
                        print(f"{phone_number} kısa süreli bir giriş çıkış yaptı.")
                    self.db.log_status_change(phone_number, "short session", last_checked, now)

                # Update status in the database
                self.db.log_status_change(phone_number, previous_status, last_checked, now)
                self.db.update_status(phone_number, current_status, last_seen)

            # Avoid printing "still online" or "still offline" messages
            else:
                pass  # Don't log anything if the status hasn't changed
        else:
            # If tracking for the first time
            if current_status == "online":
                print(colored(f"Tracking new phone number {phone_number}. Current status: {current_status}", "green"))
            elif current_status == "offline":
                print(colored(f"Tracking new phone number {phone_number}. Current status: {current_status}. Last seen: {last_seen}", "red"))
            self.db.update_status(phone_number, current_status, last_seen)
            self.db.log_status_change(phone_number, current_status, now)

    def parse_datetime(self, datetime_str):
        """Takes a datetime string and parses it into a datetime object, handling multiple formats."""
        formats = [
            "%Y-%m-%d %H:%M:%S.%f%z",  # With microseconds and timezone
            "%Y-%m-%d %H:%M:%S%z",     # With timezone but no microseconds
            "%Y-%m-%d %H:%M:%S.%f",    # With microseconds but no timezone
            "%Y-%m-%d %H:%M:%S"        # Without microseconds or timezone
        ]
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Time data '{datetime_str}' does not match any known format.")

