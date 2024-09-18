import time
import logging

class TrackerStatus:
    def __init__(self, db, session_manager):
        self.db = db
        self.session_manager = session_manager
        self.status_cache = {}
    
    def check_status(self, phone_number):
        # Sorgulama işlemi (örnek bir metot; Telegram sorgusu burada yapılır)
        status = self.session_manager.get_status(phone_number)

        if phone_number not in self.status_cache:
            self.status_cache[phone_number] = status
            self.db.save_initial_status(phone_number, status)
        else:
            previous_status = self.status_cache[phone_number]
            if previous_status != status:
                logging.info(f"Status change for {phone_number}: {previous_status} -> {status}")
                self.db.update_status(phone_number, status)
                self.status_cache[phone_number] = status

    def monitor_numbers(self, phone_numbers):
        while True:
            for number in phone_numbers:
                self.check_status(number)
            time.sleep(60)  # 60 saniyede bir kontrol eder

# Diğer gerekli importlar ve session manager, veritabanı bağlantısı gibi nesneler
# Örnek kullanımı:
# from tracker_status import TrackerStatus
# tracker = TrackerStatus(db, session_manager)
# tracker.monitor_numbers(phone_numbers)
