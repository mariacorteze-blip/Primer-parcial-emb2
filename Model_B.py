import serial
import RPi.GPIO as GPIO
import time
import os

ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    timeout=1
)

# Config del motor1
ENA = 18
IN1 = 23
IN2 = 24

# Config motor2
ENB = 19
IN3 = 5
IN4 = 6

archivo = "Model_B_dir.txt"

velocidad_actual = 50
i = 0
vel_nitro = [70, 100]

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

pwm1 = GPIO.PWM(ENA, 1000)
pwm2 = GPIO.PWM(ENB, 1000)
pwm1.start(0)
pwm2.start(0)

if not os.path.exists(archivo):
    f = open(archivo, "w")
    f.write("W")
    f.close()


def stop_all():
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    print('Motores OFF')

def avanzar():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(velocidad_actual)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(velocidad_actual)
    print("Avanzando", velocidad_actual)

def retroceder():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm1.ChangeDutyCycle(velocidad_actual)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm2.ChangeDutyCycle(velocidad_actual)
    print("Retrocediendo", velocidad_actual)

def left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(0)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(velocidad_actual)
    print("Girando IZQUIERDA", velocidad_actual)

def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(velocidad_actual)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(0)
    print("Girando DERECHA", velocidad_actual)

def nitro():
    global i, velocidad_actual
    i = i + 1
    if i >= 2:
        i = 0
    velocidad_actual = vel_nitro[i]
    
try:
    while True:
        try:
            f = open(archivo, "r")
            texto = f.read().strip()
            f.close()

            if texto != "" and texto != ultimo_comando:
                com = texto
                ultimo_comando = com
                
                if com == "W":
                    avanzar()
                elif com == "S":
                    retroceder()
                elif com == "A":
                    left()
                elif com == "D":
                    right()
                elif com == "N":
                    nitro()
                else:
                    print("Comando no reconocido:", com)
                    
        except Exception as e:
            print("Error leyendo archivo:", e)

        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            print("Distancia recibida:", data)

            try:
                distancia = float(data)
                if distancia <= 5:
                    print("¡OBSTÁCULO! Distancia:", distancia, "cm - Deteniendo robot")
                    stop_all()
            except:
                pass

        time.sleep(0.05)

except KeyboardInterrupt:
    print('Saliendo...')

finally:
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
    ser.close()
    print("Sistema cerrado")
