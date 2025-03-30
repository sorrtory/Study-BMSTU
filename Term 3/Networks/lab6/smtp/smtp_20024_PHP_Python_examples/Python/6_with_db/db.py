#!/usr/bin/python3

def printParsedLinesFromFile(string):
	lines = string.split("\n")
	for i in range(0,len(lines)-1):
		lines_cols = lines[i].split("::")
		print(str(i+1),end=") ")
		for j in range(0,len(lines_cols)):
			print(lines_cols[j],end="\t")
		print("")


import os
import datetime
now = datetime.datetime.now()
a=""

while a != "5":

	a = input("type action: 1-sel, 2-del, 3-ins, 4-upd, 5-exit: ")
	if(a=="1"):
		my_file = open("./db.txt", "r")
		my_string = my_file.read()
		my_file.close()
		printParsedLinesFromFile(my_string)

	elif(a=="3"):
		name = input("name")
		data = input("data")
		my_file = open("./db.txt", "a+")
		my_file.write(str(now.hour)+":"+str(now.minute)+":"+str(now.second)+"::"+str(now.year)+":"+str(now.month)+":"+str(now.day)+"::"+str(name)+"::"+str(data)+"\n")
		my_file.close()

	elif(a=="2"):
		my_file = open("./db.txt", "r")
		my_string = my_file.read()
		my_file.close()
		printParsedLinesFromFile(my_string)
		delNum = input("enter delete number:")
		newfilestring = ""
		my_file = open("./db.txt", "r")
		my_string = my_file.read()
		lines = my_string.split("\n")
		for i in range(0,len(lines)-1):
			if((int(delNum)-1)!=i):
				newfilestring+=lines[i]+"\n"
			#else:
				#newfilestring+="---->"+lines[i]+"\n"

		print(newfilestring)
		my_file.close()
		os.remove("db.txt")
		my_file = open("./db.txt", "a+")
		my_file.write(newfilestring)
		my_file.close()

	elif(a=="4"):
		my_file = open("./db.txt", "r")
		my_string = my_file.read()
		my_file.close()
		printParsedLinesFromFile(my_string)

		upNum = input("enter update number:")
		name = input("name")
		data = input("data")

		newfilestring = ""
		my_file = open("./db.txt", "r")
		my_string = my_file.read()
		lines = my_string.split("\n")
		for i in range(0,len(lines)-1):
			if((int(upNum)-1)!=i):
				newfilestring+=lines[i]+"\n"
			else:
				newfilestring+=str(now.hour)+":"+str(now.minute)+":"+str(now.second)+"::"+str(now.year)+":"+str(now.month)+":"+str(now.day)+"::"+str(name)+"::"+str(data)+"\n"

		print(newfilestring)
		my_file.close()
		os.remove("db.txt")
		my_file = open("./db.txt", "a+")
		my_file.write(newfilestring)
		my_file.close()







