import asyncio
from termcolor import colored
from tracker import TrackerStatus
from session_manager import SessionManager
from database import Database 
import signal
import sys
import config

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
        db = Database()  # Veritabanına bağlanma işlemi __init__ ile yapılıyor

        # Telegram Client ile oturum aç
        session_manager = SessionManager(api_id=config.API_ID, api_hash=config.API_HASH, phone=config.PHONE_NUMBER)
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
        tracker = StatusTracker(db, client)

        # Sonsuz döngü ile telefon numaralarının durumu kontrol edilir
        while True:
            tasks = []
            for phone in phone_numbers[:config.MONITOR_LIMIT]:  # Aynı anda limit kadar telefon numarası izlenir
                # Tüm telefon numaraları için async durum kontrolü yap
                tasks.append(tracker.check_phone_status(phone))
            
            # Tüm numaraların durumunu kontrol eden async görevleri paralel çalıştır
            await asyncio.gather(*tasks)

            # Belirli süre bekleme (config dosyasındaki interval değerine göre)
            await asyncio.sleep(config.CHECK_INTERVAL)

    except FileNotFoundError as e:
        # Eğer 'phones.txt' dosyası bulunamazsa
        print(colored(f"Hata: {str(e)}. 'phones.txt' dosyası bulunamadı.", "red"))

    except Exception as e:
        # Diğer hatalar
        print(colored(f"Bilinmeyen bir hata oluştu: {str(e)}", "red"))

if __name__ == "__main__":
    print(colored("Uygulama başlatılıyor... Çıkmak için Ctrl+C'ye basın.", "yellow"))
    asyncio.run(main())
