import serial
import RPi.GPIO as GPIO
import time
import os

ser=serial.Serial(
	port = '/dev/serial0',
	baudrate = 115200,
	timeout = 1
	)

	
#Config del motor1
ENA = 18
IN1 = 23
IN2 = 24

#Config motor2
ENB = 19
IN3 = 5
IN4 = 6

#Config boton
i=0
vel=[100,70]
archivo = "Model_B_dir.txt"
velocidad=50

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
#GPIO.setup(Boton,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(ENA,GPIO.OUT)
GPIO.setup(IN1,GPIO.OUT)
GPIO.setup(IN2,GPIO.OUT)

GPIO.setup(ENB,GPIO.OUT)
GPIO.setup(IN3,GPIO.OUT)
GPIO.setup(IN4,GPIO.OUT)

pwm1=GPIO.PWM(ENA,1000)
pwm2=GPIO.PWM(ENB,1000)
pwm1.start(0)
pwm2.start(0)

if not os.path.exists(archivo):
	f = open(archivo,"w")
	f.write("W")
	f.close()
	
def stop_all():
	pwm2.ChangeDutyCycle(0)
	pwm1.ChangeDutyCycle(0)
	print('Motores OFF')

def avanzar():
	GPIO.output(IN1,GPIO.HIGH)
	GPIO.output(IN2,GPIO.LOW)
	pwm1.ChangeDutyCycle(velocidad)
	GPIO.output(IN3,GPIO.HIGH)
	GPIO.output(IN4,GPIO.LOW)
	pwm2.ChangeDutyCycle(velocidad)
	print("Avanzando", velocidad)
	
def retroceder():
	GPIO.output(IN1,GPIO.LOW)
	GPIO.output(IN2,GPIO.HIGH)
	pwm1.ChangeDutyCycle(velocidad)
	GPIO.output(IN3,GPIO.LOW)
	GPIO.output(IN4,GPIO.HIGH)
	pwm2.ChangeDutyCycle(velocidad)
	print("retrocediendo", velocidad)
	
def left():
	GPIO.output(IN1,GPIO.HIGH)
	GPIO.output(IN2,GPIO.LOW)
	pwm1.ChangeDutyCycle(velocidad)
	GPIO.output(IN3,GPIO.LOW)
	GPIO.output(IN4,GPIO.LOW)
	pwm2.ChangeDutyCycle(velocidad)
	print("IZQUIERDA", velocidad)
	
def right():
	GPIO.output(IN1,GPIO.LOW)
	GPIO.output(IN2,GPIO.LOW)
	pwm1.ChangeDutyCycle(velocidad)
	GPIO.output(IN3,GPIO.HIGH)
	GPIO.output(IN4,GPIO.LOW)
	pwm2.ChangeDutyCycle(velocidad)
	print("DERECHA", velocidad)

def nitro():
	i=i+1
	if i >= 2:
		i=0
	GPIO.output(IN1,GPIO.LOW)
	GPIO.output(IN2,GPIO.HIGH)
	pwm1.ChangeDutyCycle(vel[i])
	GPIO.output(IN3,GPIO.LOW)
	GPIO.output(IN4,GPIO.HIGH)
	pwm2.ChangeDutyCycle(vel[i])
	print("Nitro")

print("Iniciamos")

try:
	while True:
		try:
			f = open(archivo,"r")
			texto = f.read().strip()
			f.close()

			if texto != "":
				com = texto

				if com == "W":
					avanzar()
				elif com == "S":
					retroceder()
				elif com =="A":
					left()
				elif com == "D":
					nitro()
				elif com == "N":
					nitro()
		except:
			print("Error leyendo archivo")

		if ser.in_waiting>0:
			data = ser.readline().decode('utf-8', errors='ignore').strip()
			print("Recibido:", data)
			try:
				distancia=float(data)
				if distancia <= 5:
					stop_all()
			except:
				pass

except KeyboardInterrupt:
	print('Saliendo')

finally:
	pwm1.stop()
	pwm2.stop()
	GPIO.cleanup()
	ser.close()
