import os
import sys
import socket
import time
from passlib.hash import pbkdf2_sha256
import RPi.GPIO as GPIO




def verify_password(password):
	file = 'hashedPass.txt'
	if os.popen('whoami').read().strip() == 'pi':
		file = '/home/pi/Documents/OpSes-Pi/hashedPass.txt'
	passFile = open(file, 'r')
	hashed = passFile.read().strip()
	return pbkdf2_sha256.verify(password, hashed)

def Open_Sesame(direction):
	#Do motor control and shit here
	print 'Opening'
	sys.stdout.flush()
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
	count = 2048
	while count > 0:
		#print StepCounter,
		#print Seq[StepCounter]

		for pin in range(0,4):
			xpin=StepPins[pin]# Get GPIO
			if Seq[StepCounter][pin]!=0:
				#print " Enable GPIO %i" %(xpin)
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)

		StepCounter += StepDir

		# If we reach the end of the sequence
		# start again
		if (StepCounter>=StepCount):
			StepCounter = 0
		if (StepCounter<0):
			StepCounter = StepCount+StepDir

		# Wait before moving on
		time.sleep(.002)
	return

def main():
	HOST = ''
	PORT = 9393
	GPIO.setmode(GPIO.BCM)
	# Physical pins 11,15,16,18
	# GPIO17,GPIO22,GPIO23,GPIO24
	StepPins = [17,22,23,24]
	direction = 1
	for pin in StepPins:
		print "Setup pins"
		GPIO.setup(pin,GPIO.OUT)
		GPIO.output(pin, False)
	 
	
	
	# Start main loop


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
	    if verify_password(password):
	    	print 'Correct Password'
	    	direction *= -1
	    	Open_Sesame(direction)
	    else:
	    	print 'Provided Password ({}) is incorrect'.format(password)

	s.close()


if __name__ == '__main__':
	main()

