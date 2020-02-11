#!/usr/bin/python

import base64
import sys
import PyPDF2
import requests
import os

pdf = open(sys.argv[1], 'rb')
pdfreader = PyPDF2.PdfFileReader(pdf)

text = ''
for i in range(0, pdfreader.numPages):
	page = pdfreader.getPage(i)
	text += page.extractText()

#may need utf-8 specified for bytes()
enc64 = base64.b64encode(bytes(text))

curlReq = "curl -X PUT \"localhost:9200/documents/pdf/42?pipeline=attachment&pretty\" -H 'Content-Type: application/json' -d' {\"data\": \"" + enc64+ "\"}'"
os.system(curlReq)