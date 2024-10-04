import asyncio
from termcolor import colored
from tracker import TrackerStatus
import signal
import sys
from session_manager import SessionManager
from database import Database
import settings  # config ismini settings olarak değiştirdik

def signal_handler(sig, frame):
    """Ctrl+C ile çıkışı sağlar."""
    print(colored("\nÇıkış yapılıyor... Uygulama kapatılıyor.", "red"))
    sys.exit(0)

# Ctrl+C sinyali yakalayıcısını ayarla
signal.signal(signal.SIGINT, signal_handler)

def load_phone_numbers(file_path='phones.txt'):
    """phones.txt dosyasından telefon numaralarını okur."""
    try:
        with open(file_path, 'r') as f:
            phone_numbers = [line.strip() for line in f.readlines() if line.strip()]
        return phone_numbers
    except FileNotFoundError:
        print(colored(f"Hata: {file_path} dosyası bulunamadı.", "red"))
        return []

async def main():
    """Ana kontrol fonksiyonu."""
    try:
        # Veritabanına bağlan
        db = Database()

        # Telegram Client ile oturum aç
        session_manager = SessionManager(api_id=settings.API_ID, api_hash=settings.API_HASH, phone=settings.PHONE_NUMBER)
        await session_manager.start_session()
        client = session_manager.get_client()

        # Telefon numaralarını yükle
        phone_numbers = load_phone_numbers()

        # Eğer numara yüklenmezse hata ver
        if not phone_numbers:
            print(colored("Hiçbir telefon numarası yüklenemedi. 'phones.txt' dosyasını kontrol edin.", "red"))
            return

        print(colored("Telefon numaraları başarıyla yüklendi. Durumlar takip ediliyor...", "green"))

        # Tracker başlat
        tracker = TrackerStatus(db, client, limit=settings.MONITOR_LIMIT)

        # Telefon numaralarının durumunu takip et
        await tracker.monitor_numbers(phone_numbers)

    except FileNotFoundError as e:
        print(colored(f"Hata: {str(e)}. 'phones.txt' dosyası bulunamadı.", "red"))

    except Exception as e:
        print(colored(f"Bilinmeyen bir hata oluştu: {str(e)}", "red"))

if __name__ == "__main__":
    print(colored("Uygulama başlatılıyor... Çıkmak için Ctrl+C'ye basın.", "yellow"))
    asyncio.run(main())


