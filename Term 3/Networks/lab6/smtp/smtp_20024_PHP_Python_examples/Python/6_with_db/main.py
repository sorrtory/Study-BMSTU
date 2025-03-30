#!/usr/bin/python3

import os
a = ""

while a != "3":

	a = input("edit DB - 1\nsendmail - 2\nexit - 3\n")

	if(a=="1"):
		os.system("./db.py")
	elif(a=="2"):
		os.system("./mailsend.py")
