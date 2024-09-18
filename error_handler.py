import sqlite3
import os
from datetime import datetime

# Bellekte saklanan son görülen zamanları izlemek için bir dictionary
last_seen_cache = {}

# Database connection helper
def connect_to_db(db_name="phone_status.db"):
    if not os.path.exists(db_name):
        print(f"Database '{db_name}' not found, creating new one.")
    connection = sqlite3.connect(db_name)
    return connection

# Ensure that the phone_status table exists
def ensure_table_exists(connection):
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone_status (
            phone_number TEXT PRIMARY KEY,
            last_seen TEXT
        )
    ''')
    connection.commit()

# Update or insert the phone number into the table
def update_phone_status(connection, phone_number, online=False):
    cursor = connection.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the phone number exists in the table and retrieve the last_seen
    cursor.execute('SELECT last_seen FROM phone_status WHERE phone_number = ?', (phone_number,))
    row = cursor.fetchone()

    if row:
        last_seen = row[0]
        # Eğer online ise ya da last_seen zamanında bir değişiklik varsa, yazdır
        if online:
            print(f"{phone_number} is online.")
            cursor.execute('UPDATE phone_status SET last_seen = ? WHERE phone_number = ?', (current_time, phone_number))
        elif last_seen != current_time:
            cursor.execute('UPDATE phone_status SET last_seen = ? WHERE phone_number = ?', (current_time, phone_number))
            print(f"Updated phone number {phone_number} with new last_seen time {current_time}.")
            # Cache'i güncelle
            last_seen_cache[phone_number] = current_time
        else:
            # Eğer last_seen aynı ise yazdırmayı atla
            print(f"No change for {phone_number}, last seen remains the same.")
    else:
        # Eğer telefon numarası yoksa yeni kaydı ekle
        cursor.execute('INSERT INTO phone_status (phone_number, last_seen) VALUES (?, ?)', (phone_number, current_time))
        print(f"Inserted phone number {phone_number} with last_seen time {current_time}.")
        # Cache'e yeni kaydı ekle
        last_seen_cache[phone_number] = current_time

    connection.commit()

# Process the phone numbers from the phones.txt file
def process_phone_numbers(connection, phones_file='phones.txt'):
    try:
        with open(phones_file, 'r') as file:
            phone_numbers = file.readlines()
        
        for phone_number in phone_numbers:
            phone_number = phone_number.strip()
            if phone_number:
                # Bellekte saklanan last_seen zamanını kontrol et
                if phone_number in last_seen_cache and last_seen_cache[phone_number] == datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
                    # Eğer değişiklik yoksa yazdırma
                    continue
                update_phone_status(connection, phone_number)
    except FileNotFoundError:
        print(f"File '{phones_file}' not found. Please ensure it exists in the current directory.")
    except Exception as e:
        print(f"An error occurred while processing phone numbers: {str(e)}")

# Main function to execute the database update process
def main():
    connection = connect_to_db()

    # Ensure the table exists
    ensure_table_exists(connection)

    # Process phone numbers
    process_phone_numbers(connection)

    # Close the connection after everything is done
    connection.close()

if __name__ == "__main__":
    main()
