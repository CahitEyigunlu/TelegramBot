import asyncio
from telethon import TelegramClient
import signal

# Telegram API kimlik bilgileri
api_id = 23185610  # Sağladığınız API ID
api_hash = '9ddb92cd807a734b9bba85500e2dd742'  # Sağladığınız API Hash
phone = '+905074510000'  # Kendi Telegram hesabınıza ait telefon numarası

client = TelegramClient('session_main', api_id, api_hash)

async def initial_login():
    await client.start(phone)  # İlk oturum açma işlemi
    print("Client connected and session saved.")

async def check_online_status(number):
    try:
        print(f"Tracking number: {number}")
        user = await client.get_entity(number)

        # Kullanıcının çevrimiçi durumunu kontrol edin
        if user.status is not None:
            if isinstance(user.status, telethon.tl.types.UserStatusOnline):
                print(f"{number} is online.")
            elif isinstance(user.status, telethon.tl.types.UserStatusOffline):
                print(f"{number} is offline.")
            else:
                print(f"{number}'s status is hidden.")
        else:
            print(f"{number}'s status is not available.")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    # Örnek numara listesi
    numbers_to_track = ['+905074510000', '+905074520000']

    # İlk oturumu başlatın
    await initial_login()

    # Her numara için online durumu kontrol edin
    tasks = [check_online_status(number) for number in numbers_to_track]
    await asyncio.gather(*tasks)

    # Oturum kapatılmadan önce işlemleri tamamlayın
    await client.disconnect()

# Programı CTRL+C ile durdurabilmek için bir sinyal yakalayıcı ekleyin
def handle_exit(loop):
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), lambda: asyncio.create_task(shutdown(loop)))

async def shutdown(loop):
    """Programın düzgün bir şekilde durdurulması için kapanış işlemleri."""
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

# Olay döngüsünü çalıştır ve sinyal yakalamayı ekleyin
loop = asyncio.get_event_loop()
handle_exit(loop)

try:
    loop.run_until_complete(main())
finally:
    loop.close()
