import asyncio
from telethon import TelegramClient
from termcolor import colored
from sqlite_db import SQLiteDB
import datetime  # datetime modülü yüklü

class SessionManager:

    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = TelegramClient('session_main', api_id, api_hash)

    async def start_session(self):
        await self.client.start(self.phone)

    def get_client(self):
        return self.client

    async def close_session(self):
        await self.client.disconnect()
        self.log_activity("Session closed.")
        self.db.log_status_change(self.phone, "disconnected", datetime.datetime.now())


    def log_activity(self, message):
        """Verilen mesajı logs/activity.log dosyasına kaydeder."""
        with open("logs/activity.log", "a") as log_file:
            log_file.write(f"{message}\n")

# Main function to start session (example)
async def main():
    api_id = 'your_api_id'
    api_hash = 'your_api_hash'
    phone = 'your_phone_number'

    session_manager = SessionManager(api_id, api_hash, phone)
    await session_manager.start_session()

    # Oturum başlatıldıktan sonra işlemler yapılabilir
    # await session_manager.get_client().get_me() gibi
    # Oturumu kapatmak için:
    await session_manager.close_session()

if __name__ == "__main__":
    asyncio.run(main())
