#!/usr/bin/python3

import socket
import sys
import select
import random

def firstmsg(newcon):
	newcon.send("Welcome to the chat server (version March 1 2021)\r\n".encode())
	newcon.send("type \"roll\" to roll a dice\r\n".encode())
	newcon.send("type \"online\" to see all online users\r\n\n".encode())

def setupfacts(facts):
	facts.append("In Africa, every 60 seconds, a minute passes")
	facts.append("In China, every 120 seconds, two minutes passes")
	facts.append("100% of people who drink water dies")
	facts.append("The world record for a human holding its breath is 22 minutes")

def findname(soc,names):
	count = 0
	for x in names:
		if x[0] == soc:
			return count
		count += 1
	return 0

def main(argv):
	# set port number
	# default is 32342 if no input argument
	if len(argv) == 2:
		port = int(argv[1])
	else:
		port = 32342

	# create socket and bind
	sockfd = socket.socket()
	sockfd.bind(('localhost',port))

	# set socket listening queue
	sockfd.listen(10)
	names = []
	read = []

	# add the listening socket to the READ socket list
	read.append(sockfd)
	names.append([sockfd, "server", 'sample message'])

	# create an empty WRITE socket list
	write = []

	# set up quick facts
	facts = []
	setupfacts(facts)

	# start the main loop
	while True:

		# use select to wait for any incoming connection requests or
		# incoming messages or 10 seconds
		r,w,e = select.select(read,[],[],2.0)

		# if has incoming activities
		try:

			# for each socket in the READ ready list
			for reader in r:

				# if the listening socket is ready
				# that means a new connection request
				# accept that new connection request
				# add the new client connection to READ socket list
				# add the new client connection to WRITE socket list
				if reader is sockfd:
					newcon, addr = sockfd.accept()
					newcon.send("please type your name\r\n".encode())
					newcon.settimeout(5.0)
					try:
						nameobj = newcon.recv(1024)
						name = ""
						while nameobj != "\r\n".encode():
							name += nameobj.decode()
							nameobj = newcon.recv(1024)
					except socket.timeout:
						newcon.send("timeout".encode())
						continue
					firstmsg(newcon)
					newcon.settimeout(None)
					read.append(newcon)
					write.append(newcon)
					names.append([newcon, name, ''])
					print("new connection established", addr)
					welcomemsg = name+" has joined the chat\r\n\n"
					for writer in write:
						writer.send(welcomemsg.encode())

				# else is a client socket being ready
				# that means a message is waiting or
				# a connection is broken
				# if a new message arrived, send to everybody
				# except the sender
				# if broken connection, remove that socket from READ
				# and WRITE lists
				else:
					msg = reader.recv(1024)
					pos = findname(reader,names)
					name = names[pos][1]
					if msg:
						if msg == "\r\n".encode():
							if names[pos][2] == "roll":
								dice = random.randint(1,6)
								message = "\r\n"+name+" rolls a dice and gets "+str(dice)
								message += "\r\n"
								for writer in write:
									writer.send(message.encode())
							elif names[pos][2]=="online":
								for namer in names:
									namerr = namer[1]+"\r\n"
									reader.send(namerr.encode())
								total = "total "+str(len(names))+" users online\r\n\n"
								reader.send(total.encode())
							else:
								message = "\r\n"+name + ": "+ names[pos][2] + "\r\n"
								for writer in write:
									if writer is not reader:
										writer.send(message.encode())
							print(name," sent a message")
							names[pos][2] = ''
						else:
							names[pos][2] += msg.decode()
					else:
						print(name," left")
						read.remove(reader)
						write.remove(reader)
						message = name + " has left the chat\r\n"
						names.remove(names[pos])
						for writer in write:
							if writer is not reader:
								writer.send(message.encode())
		# else did not have activity for 10 seconds,
		# just print out "Idling"
		except socket.error as emsg:
			print("socket accept error:", emsg)
			exit(1)
		if not (r or w or e):
			print("Idling")
			funfact = "Do you know that "+facts[random.randint(0,3)]+"\r\n"
			for writer in write:
				writer.send(funfact.encode())
			continue

if __name__ == '__main__':
	if len(sys.argv) > 2:
		print("Usage: chatserver [<Server_port>]")
		sys.exit(1)
	main(sys.argv)
