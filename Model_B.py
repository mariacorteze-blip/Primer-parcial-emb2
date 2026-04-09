import serial
import RPi.GPIO as GPIO
import time
import os


ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    timeout=1
)


ENA = 18
IN1 = 23
IN2 = 24

ENB = 19
IN3 = 5
IN4 = 6

velocidad = 50
i = 0
vel = [100, 70] 
archivo = "Model_B_dir.txt"

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
    with open(archivo, "w") as f:
        f.write("W")  # Dirección inicial: adelante


def stop_all():
    """Detiene ambos motores"""
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    print('Motores OFF')

def avanzar():
    """Avanza en línea recta"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(velocidad)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(velocidad)
    print(f"Avanzando - Velocidad: {velocidad}%")

def retroceder():
    """Retrocede en línea recta"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm1.ChangeDutyCycle(velocidad)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm2.ChangeDutyCycle(velocidad)
    print(f"Retrocediendo - Velocidad: {velocidad}%")

def left():
    """Gira a la izquierda (motor derecho avanza, izquierdo quieto)"""
    GPIO.output(IN1, GPIO.LOW)   # Motor izquierdo apagado
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(0)
    GPIO.output(IN3, GPIO.HIGH)  # Motor derecho avanza
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(velocidad)
    print(f"Girando IZQUIERDA - Velocidad: {velocidad}%")

def right():
    """Gira a la derecha (motor izquierdo avanza, derecho quieto)"""
    GPIO.output(IN1, GPIO.HIGH)  # Motor izquierdo avanza
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(velocidad)
    GPIO.output(IN3, GPIO.LOW)   # Motor derecho apagado
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(0)
    print(f"Girando DERECHA - Velocidad: {velocidad}%")

def nitro():
    global i  
    i = i + 1
    if i >= 2:
        i = 0
    
    
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm1.ChangeDutyCycle(vel[i])
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm2.ChangeDutyCycle(vel[i])
    print(f"MODO NITRO ACTIVADO - Velocidad: {vel[i]}%")


print("Sistema iniciado - Esperando comandos...")
print("Comandos disponibles:")
print("  W = Avanzar")
print("  S = Retroceder")
print("  A = Girar izquierda")
print("  D = Girar derecha")
print("  N = Modo nitro")
print("  (También recibe distancia por UART para detención automática)")
print("-" * 50)

try:
    while True:
        # Leer comando desde archivo
        try:
            with open(archivo, "r") as f:
                texto = f.read().strip()
            
            if texto:
                com = texto
                
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
                    
        except Exception as e:
            print(f"Error leyendo archivo: {e}")

       
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Recibido por UART: {data}")
            
            try:
                distancia = float(data)
                if distancia <= 5: 
                    print(f"¡OBSTÁCULO! Distancia: {distancia} cm - Deteniendo robot")
                    stop_all()
            except ValueError:
                pass

       
        time.sleep(0.05)

except KeyboardInterrupt:
    print('\nPrograma detenido por el usuario')

finally:
    print("Limpiando recursos...")
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
    ser.close()
    print("Sistema cerrado correctamente")
