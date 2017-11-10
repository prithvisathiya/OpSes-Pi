import os
import sys
import socket
import time
from passlib.hash import pbkdf2_sha256


def verify_password(password):
	passFile = open('hashedPass.txt', 'r')
	hashed = passFile.read().strip()
	return pbkdf2_sha256.verify(password, hashed)

def Open_Sesame():
	#Do motor control and shit here
	print 'Opening'
	return

def main():
	HOST = ''
	PORT = 9393
	 
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


	while 1:
	    #wait to accept a connection - blocking call
	    conn, addr = s.accept()
	    print 'Connected with ' + addr[0] + ':' + str(addr[1])
	    password = conn.recv(1024)
	    if verify_password(password):
	    	print 'Correct Password'
	    	Open_Sesame()
	    else:
	    	print 'Provided Password ({}) is incorrect'.format(password)

	s.close()


if __name__ == '__main__':
	main()

