import asyncio
from telethon import TelegramClient
from termcolor import colored

class SessionManager:
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = TelegramClient('session_main', api_id, api_hash)

    async def start_session(self):
        """Telegram oturumunu başlatır ve kullanıcı doğrulamasını gerçekleştirir."""
        await self.client.start(self.phone)
        print(colored("Client connected and session saved.", "green"))
        self.log_activity("Client connected and session saved.")

    async def close_session(self):
        """Oturumu kapatır ve bağlantıyı düzgün şekilde sonlandırır."""
        await self.client.disconnect()
        print(colored("Session closed.", "yellow"))
        self.log_activity("Session closed.")

    def get_client(self):
        """Client'i döner."""
        return self.client

    def log_activity(self, message):
        """Verilen mesajı logs/activity.log dosyasına kaydeder."""
        with open("logs/activity.log", "a") as log_file:
            log_file.write(f"{message}\n")
