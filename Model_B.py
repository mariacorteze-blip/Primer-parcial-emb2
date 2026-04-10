import serial
import RPi.GPIO as GPIO
import time
import os
import threading  

ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    timeout=0.1  )

ENA = 18
IN1 = 23
IN2 = 24
ENB = 19
IN3 = 5
IN4 = 6

i = 0
vel = [70, 100]
archivo = "Model_B_dir.txt"
ultima_distancia = 100  
robot_detenido = False  

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
        f.write("W")

def stop_all():
    global robot_detenido
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    robot_detenido = True
    print('Motores OFF')

def reanudar():
    global robot_detenido
    robot_detenido = False
    print("Obstáculo superado - Reanudando movimiento")

def avanzar():
    global robot_detenido
    if robot_detenido:
        return  
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(vel[i])
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(vel[i])
    print(f"Avanzando - Velocidad: {vel[i]}%")

def retroceder():
    global robot_detenido
    if robot_detenido:
        return
    
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm1.ChangeDutyCycle(vel[i])
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm2.ChangeDutyCycle(vel[i])
    print(f"Retrocediendo - Velocidad: {vel[i]}%")

def left():
    global robot_detenido
    if robot_detenido:
        return
    
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(0)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(vel[i])
    print(f"Girando IZQUIERDA - Velocidad: {vel[i]}%")

def right():
    global robot_detenido
    if robot_detenido:
        return
    
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm1.ChangeDutyCycle(vel[i])
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(0)
    print(f"Girando DERECHA - Velocidad: {vel[i]}%")

def nitro():
    global i
    i = i + 1
    if i >= 2:
        i = 0
    print(f"Modo Nitro - Velocidad cambiada a: {vel[i]}%")

def leer_uart():
    global ultima_distancia, robot_detenido
    
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    print(f"[UART] Distancia recibida: {data} cm")
                    
                    try:
                        distancia = float(data)
                        ultima_distancia = distancia
                        
                        # Detener si hay obstáculo
                        if distancia <= 5:
                            if not robot_detenido:
                                print(f"OBSTÁCULO! Distancia: {distancia} cm - Deteniendo robot")
                                stop_all()
                        else:
                            # Si el obstáculo ya no está, reanudar
                            if robot_detenido and distancia > 5:
                                print(f"Obstáculo superado - Reanudando robot")
                                robot_detenido = False
                                
                    except ValueError:
                        pass
        except Exception as e:
            print(f"Error en lectura UART: {e}")
        
        time.sleep(0.01) 
def main():
    global robot_detenido
    
    print("=" * 50)
    print("SISTEMA INICIADO")
    print("Comandos disponibles:")
    print("  W = Avanzar")
    print("  S = Retroceder")
    print("  A = Girar izquierda")
    print("  D = Girar derecha")
    print("  N = Modo nitro")
    print("")
    print("El robot se detendrá automáticamente si hay un obstáculo a ≤ 5cm")
    print("=" * 50)
    
    # Iniciar hilo 
    hilo_uart = threading.Thread(target=leer_uart, daemon=True)
    hilo_uart.start()
    print("Hilo de lectura UART iniciado")
    
    ultimo_comando = None  
    try:
        while True:
            try:
                with open(archivo, "r") as f:
                    texto = f.read().strip()
                
                if texto and texto != ultimo_comando:
                    com = texto
                    ultimo_comando = com
                    
                    print(f"\n[COMANDO] Ejecutando: {com}")
                    
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
                        print(f"Comando no reconocido: {com}")
                        
            except Exception as e:
                print(f"Error leyendo archivo: {e}")
            
            if robot_detenido:
                print(f"Robot DETENIDO - Última distancia: {ultima_distancia} cm", end="\r")
            
            time.sleep(0.05)  
			
    except KeyboardInterrupt:
        print('\n\nPrograma detenido por el usuario')
    
    finally:
        print("Limpiando recursos...")
        pwm1.stop()
        pwm2.stop()
        GPIO.cleanup()
        ser.close()
        print("Sistema cerrado correctamente")

if __name__ == "__main__":
    main()
