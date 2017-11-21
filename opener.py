import os
import sys
import socket
import time
import json
import base64
from Crypto.Cipher import AES
from passlib.hash import pbkdf2_sha256
OnPI = False
if os.popen('whoami').read().strip() == 'pi':
	OnPI = True
if OnPI:
	import RPi.GPIO as GPIO


def decrypt_password(password):
	password = base64.b64decode(password)
	file = 'mySecretKey.txt'
	if OnPI:
		file = '/home/pi/Documents/OpSes-Pi/mySecretKey.txt'
	keyFile = open(file, 'r')
	key = base64.b64decode(keyFile.read().strip())
	keyFile.close()
	iv = password[0:16]
	password = password[16:]
	cipher = AES.new(key, AES.MODE_CBC, iv)
	decPass = cipher.decrypt(password).strip()
	return decPass


def verify_password(password):
	file = 'hashedPass.txt'
	if OnPI:
		file = '/home/pi/Documents/OpSes-Pi/hashedPass.txt'
	passFile = open(file, 'r')
	hashed = passFile.read().strip()
	passFile.close()
	return pbkdf2_sha256.verify(password, hashed)

def Open_Sesame(direction):
	print 'Opening'
	sys.stdout.flush()
	if OnPI:
		StepPins = [17,22,23,24]
		Seq = [[1,0,0,1],
		       [1,0,0,0],
		       [1,1,0,0],
		       [0,1,0,0],
		       [0,1,1,0],
		       [0,0,1,0],
		       [0,0,1,1],
		       [0,0,0,1]]
		        
		StepCount = len(Seq)
		StepDir = direction * 2
		 
		# Initialise variables
		StepCounter = 0
		count = 512
		while count > 0:
			for pin in range(0,4):
				xpin=StepPins[pin]# Get GPIO
				if Seq[StepCounter][pin]!=0:
					#print " Enable GPIO %i" %(xpin)
					GPIO.output(xpin, True)
				else:
					GPIO.output(xpin, False)

			StepCounter += StepDir

			if (StepCounter>=StepCount):
				StepCounter = 0
			if (StepCounter<0):
				StepCounter = StepCount+StepDir
			count -= 1
			time.sleep(.002)
		for pin in StepPins:
			GPIO.output(pin, False)
	return

def main():
	HOST = ''
	PORT = 9393
	if OnPI:
		GPIO.setmode(GPIO.BCM)
		# Physical pins 11,15,16,18
		# GPIO17,GPIO22,GPIO23,GPIO24
		StepPins = [17,22,23,24]
		direction = 1
		for pin in StepPins:
			print "Setup pins"
			GPIO.setup(pin,GPIO.OUT)
			GPIO.output(pin, False)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	print 'Socket created'

	#Bind socket to local host and port
	try:
	    s.bind((HOST, PORT))
	except socket.error as msg:
	    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	    sys.exit()

	print 'Socket bind complete'

	#Start listening on socket
	s.listen(5)
	print 'Socket now listening'

	sys.stdout.flush()

	while 1:
	    #wait to accept a connection - blocking call
	    conn, addr = s.accept()
	    print 'Connected with ' + addr[0] + ':' + str(addr[1])
	    sys.stdout.flush()
	    password = conn.recv(1024)

	    try:
	    	password = decrypt_password(password)	
	    except Exception as e:
	    	print e 
	    	sys.stdout.flush()
	    	continue
	    
	    if verify_password(password):
	    	print 'Correct Password'
	    	direction *= -1
	    	Open_Sesame(direction)
	    else:
	    	print 'Provided Password ({}) is incorrect'.format(password)

	s.close()


if __name__ == '__main__':
	main()

