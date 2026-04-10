import serial
import RPi.GPIO as GPIO
import time
import os

ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    timeout=0.1
)

Boton = 17
archivo = "velocidad2.txt"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Boton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

velocidad_actual = -1
last_button_state = 0

if not os.path.exists(archivo):
    with open(archivo, "w") as f:
        f.write("50")

print("Sistema iniciado.")

try:
    while True:
        try:
            with open(archivo, "r") as f:
                contenido = f.read().strip()
                if contenido:
                    nueva_v = int(contenido)
                    nueva_v = max(0, min(100, nueva_v))
                    
                    if nueva_v != velocidad_actual:
                        velocidad_actual = nueva_v
                        mensaje = str(velocidad_actual) + "\n"
                        ser.write(mensaje.encode())
                        print(f"Enviando nueva velocidad: {velocidad_actual}")
        except Exception as e:
            print("Error leyendo archivo:", e)

        if ser.in_waiting > 0:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()
            if linea:
                print("Tiva dice:", linea)

        button_state = GPIO.input(Boton)
        if button_state == 1 and last_button_state == 0:
            print("Enviando comando Buzzer")
            ser.write(b"buzzer\n")
            time.sleep(0.2)
        last_button_state = button_state

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Saliendo...")
finally:
    GPIO.cleanup()
    ser.close()
