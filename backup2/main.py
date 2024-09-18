import asyncio
from termcolor import colored
from tracker import StatusTracker  # tracker.py içinden StatusTracker sınıfını içe aktar
import signal
import sys
from session_manager import SessionManager
from sqlite_db import SQLiteDB  # SQLiteDB sınıfını içe aktar

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
        db = SQLiteDB()  # Veritabanına bağlanma işlemi __init__ ile yapılıyor

        # Telegram Client ile oturum aç
        session_manager = SessionManager(api_id=1234567, api_hash="your_api_hash", phone="+905432348436")
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
            for phone in phone_numbers:
                # Tüm telefon numaraları için async durum kontrolü yap
                tasks.append(tracker.check_phone_status(phone))
            
            # Tüm numaraların durumunu kontrol eden async görevleri paralel çalıştır
            await asyncio.gather(*tasks)

            # 10 saniye bekleme süresi
            await asyncio.sleep(10)

    except FileNotFoundError as e:
        # Eğer 'phones.txt' dosyası bulunamazsa
        print(colored(f"Hata: {str(e)}. 'phones.txt' dosyası bulunamadı.", "red"))

    except Exception as e:
        # Diğer hatalar
        print(colored(f"Bilinmeyen bir hata oluştu: {str(e)}", "red"))

if __name__ == "__main__":
    print(colored("Uygulama başlatılıyor... Çıkmak için Ctrl+C'ye basın.", "yellow"))
    asyncio.run(main())
