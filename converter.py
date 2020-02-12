#!/usr/bin/python

import base64
import sys
import PyPDF2
import requests
import os
import json

def init():

	confirm = str(raw_input("Any existing cfg.json file will be cleared. Continue? ['yes' to contine]  ")) #confirm making new file
	if not confirm == "yes":
		exit()

	print("Making cfg.json file.")
	cfg = { 'host' : 'localhost' , 'port' : 9200 , 'id' : 0 , 'uname': '', 'pwd': ''} #format and write the default data to json
	with open("cfg.json", "w+") as f:
		f.write(json.dumps(cfg))

	configSettings() #configure the settings to instance

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
		cfg = json.dumps({'host':cfg.get('host'), 'port':cfg.get('port'), 'id': id, 'uname':cfg.get('uname'), 'pwd': cfg.get('pwd') })
		f.write(cfg)

	return str(id)

def processPDF():
	text = ''
	pdf = open(sys.argv[1], 'rb') #open the pdf file and load it with the PyPDF
	pdfreader = PyPDF2.PdfFileReader(pdf)

	for i in range(0, pdfreader.numPages): #append all pages to the text string
		page = pdfreader.getPage(i)
		text += page.extractText()
	return text #return full pdf doc

def loadSettings():
	cfg = None
	try: #open file to read as a check
		with open("cfg.json", "r") as f:
			cfg = json.load(f)
	except IOError: #if it fails generate the file with defaults for elasticsearch
		print("Missing cfg.json file, new config file has been created.")
		cfg = { 'host' : 'localhost' , 'port' : 9200 , 'id' : 0, 'uname': '', 'pwd': '' }
		with open("cfg.json", "w+") as f:
			f.write(json.dumps(cfg))

	return cfg

def configSettings():
	cfg = loadSettings() #load current settings

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

	uname = str(raw_input("Enter username: ")) #get new uname and check it
	if(uname != ''):
		print("Username updated");
	else:
		uname = cfg.get('uname')

	pwd = str(raw_input("Enter Password: ")) #get new password and check it
	if(pwd != ''):
		print("Password updated");
	else:
		pwd = cfg.get('pwd')

	seed = None
	try: #get base seed value or pass if invalid
		seed = int(raw_input("Enter int for starting seed id: "))
		print("Base seed value updated") 
	except ValueError:
		seed = cfg.get('id')


	#load information into config dict and write it to json file
	cfg_dict = { 'host' : host , 'port' : port , 'id' : seed, 'uname': uname, 'pwd' : pwd}
	cfg =  json.dumps(cfg_dict)

	with open("cfg.json", "w+") as f:
		f.write(cfg)
	
#-------------------------------------------------------------------------
doctype = 'pdf' #default type is PDF
text = '' #placeholder for text output
cfg = loadSettings(); #load the cfg.json settings

#get the arg and act with it
if(sys.argv[1] == "--config"): #configure settings
	configSettings()
	exit()

elif(sys.argv[1] == "--init"): #make fresh settings
	init()
	exit()

elif(sys.argv[1].endswith(".pdf")):
	text = processPDF()
	doctype = 'pdf'

else: #default exit gracefully
	print("No valid file or command specified.")
	exit()

id = getID() #get the current ID to avoid overlap

#may need utf-8 specified for bytes()
enc64 = base64.b64encode(bytes(text)) #encode pdf in base64

curlReq = ''
#format and make http call to elasticsearch
if(cfg.get('uname') == '' or cfg.get('pwd') == ''):
	curlReq = "curl -XPUT \""+cfg.get('host')+":"+str(cfg.get('port'))+"/documents/" + doctype + "/" + str(id) +"?pipeline=attachment&pretty\" -H 'Content-Type: application/json' -d' {\"data\": \"" + enc64+ "\"}'"
else:
	curlReq = "curl --user "+cfg.get('uname') + ":" + cfg.get('pwd') + " -XPUT \""+cfg.get('host')+":"+str(cfg.get('port'))+"/documents/" + doctype + "/" + str(id) +"?pipeline=attachment&pretty\" -H 'Content-Type: application/json' -d' {\"data\": \"" + enc64+ "\"}'"
os.system(curlReq)