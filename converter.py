#!/usr/bin/python

import base64
import sys
import PyPDF2
import requests
import os
import json

def init():

	confirm = str(raw_input("Any existing cfg.json file will be cleared. Continue? ['yes' to contine]  "))
	if not confirm == "yes":
		exit()

	print("Making cfg.json file.")
	cfg = { 'host' : 'localhost' , 'port' : 9200 , 'id' : 0 }
	with open("cfg.json", "w+") as f:
		f.write(json.dumps(cfg))

	configSettings()

def getID():
	cfg = None
	try: #open file to read as a check
		with open("cfg.json", "r") as f:
			cfg = json.load(f)
	
	except IOError: #if it fails generate the file and put in seed val of 0
		print("Failed to read cfg.json file. Please run this script with the flag --config to configure settings.")
		exit()

	id = cfg.get('id') + 1
	
	#write updated seed to file
	with open("cfg.json", "w+") as f:
		cfg = json.dumps({'host':cfg.get('host'), 'port':cfg.get('port'), 'id': id})
		f.write(cfg)

	return str(id)

def processPDF():
	text = ''
	pdf = open(sys.argv[1], 'rb')
	pdfreader = PyPDF2.PdfFileReader(pdf)

	for i in range(0, pdfreader.numPages):
		page = pdfreader.getPage(i)
		text += page.extractText()
	return text

def loadSettings():
	cfg = None
	try: #open file to read as a check
		with open("cfg.json", "r") as f:
			cfg = json.load(f)
	except IOError: #if it fails generate the file
		print("Missing cfg.json file, new config file has been created.")
		cfg = { 'host' : 'localhost' , 'port' : 9200 , 'id' : 0 }
		with open("cfg.json", "w+") as f:
			f.write(json.dumps(cfg))

	return cfg

def configSettings():
	cfg = loadSettings()

	host = str(raw_input("Enter host adress: ")) #get new host and check it
	if(host != ''):
		print("Host address updated");
	else:
		host = cfg.get('host')

	port = None
	try: #get port or pass if invalid
		port = int(raw_input("Enter port number: "))
		print("Port value updated") 
	except ValueError:
		port = cfg.get('port')

	seed = None
	try: #get base seed value or pass if invalid
		seed = int(raw_input("Enter int for starting seed id: "))
		print("Base seed value updated") 
	except ValueError:
		seed = cfg.get('seed')

	cfg_dict = { 'host' : host , 'port' : port , 'id' : seed }
	cfg =  json.dumps(cfg_dict)

	with open("cfg.json", "w+") as f:
		f.write(cfg)
	
#-------------------------------------------------------------------------
doctype = 'pdf' #default type is PDF
text = ''
cfg = loadSettings();

if(sys.argv[1] == "--config"):
	configSettings()
	exit()

elif(sys.argv[1].endswith(".pdf")):
	text = processPDF()
	doctype = 'pdf'

elif(sys.argv[1] == "--init"):
	init()
	exit()

else:
	print("No valid file or command specified.")
	exit()

id = getID()

#may need utf-8 specified for bytes()
enc64 = base64.b64encode(bytes(text))

curlReq = "curl -X PUT \""+cfg.get('host')+":"+str(cfg.get('port'))+"/documents/" + doctype + "/" + str(id) +"?pipeline=attachment&pretty\" -H 'Content-Type: application/json' -d' {\"data\": \"" + enc64+ "\"}'"
print (curlReq)
os.system(curlReq)

