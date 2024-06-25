import threading
import time
import serial
import msvcrt  # Windows için klavye okuma modülü, eğer Linux kullanıyorsanız başka bir modül gerekebilir.
from acrome.premium import *

# Seri port ayarları
SERIAL_PORT = 'COM6'  # Değiştirmeniz gerekebilir
BAUD_RATE = 115200

# Frekans ayarları
KEYBOARD_READ_INTERVAL = 0.01  # Klavye okuma aralığı (10ms)
SERIAL_COMM_INTERVAL = 0.005  # Seri port iletişim aralığı (5ms)


global_setpoint = 0
keyboard_input = 0

def read_keyboard():
    print("Klavyeden ok tuşları için veri alma başlatıldı (Çıkmak için 'q' tuşuna basın).")
    while True:
        time.sleep(KEYBOARD_READ_INTERVAL)
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'q':  # Çıkış için 'q' tuşu
                print("Çıkış yapılıyor...")
                break
            elif key == b'K':  # Sol ok tuşu
                keyboard_input = -1
            elif key == b'M':  # Sağ ok tuşu
                keyboard_input = 1

def update_setpoint():
    global_setpoint += keyboard_input

def blue_communication(setpoint):
    m = Master(SERIAL_PORT)
    m.attach(Premium(0))
    while True:
        time.sleep(SERIAL_COMM_INTERVAL)  # 5ms bekleme
        m.set_variables(0, [[Index.GoalPosition, setpoint]])
        

# Thread'leri başlat
keyboard_thread = threading.Thread(target=read_keyboard)
serial_thread = threading.Thread(target=blue_communication ,args=(global_setpoint))

keyboard_thread.start()
serial_thread.start()

keyboard_thread.join()
serial_thread.join()