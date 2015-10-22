import httplib
import socket
import re
import ssl
from urlparse import urlparse 
from slacker import Slacker

def bcolor(text):
    if(text=='header'):
    	return '\033[95m'
    if(text=='note'):
    	return '\033[94m'
    if(text=='okay'):
    	return '\033[92m'
    if(text=='warning'):
    	return '\033[93m'
    if(text=='fail'):
    	return '\033[91m'
    if(text=='ENDC'):
    	return '\033[0m'
    if(text=='BOLD'):
    	return '\033[1m'
    if(text=='UNDERLINE'):
    	return '\033[4m'

def is_website_online(host):
    try:
        socket.gethostbyname(host)
    except socket.gaierror:
        return False
    else:
        return True

def colourise(text,colour):
	if(colour=='fail'):
		# Post to your chosen list, such as Slack
		slack = Slacker('')
		slack.chat.post_message('#attitude-devel',text,'Ping Checker failed')
	return bcolor(colour)+text+bcolor('ENDC')

def checkUrl(url,text,display=True):
	p = urlparse(url)
	if display:
		print url
	if(is_website_online(p.netloc)):
		if display:
			print colourise('	DNS check OK','okay')
		try:
			if(p.scheme=='http'):
				conn = httplib.HTTPConnection(p.netloc,timeout=20)
			else:
				ctx = ssl.create_default_context()
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
				conn = httplib.HTTPSConnection(p.netloc,context=ctx,timeout=10)
			conn.request('HEAD', p.path)
			resp = conn.getresponse()
			if(resp.status<400):
				if(resp.status==200):
					print colourise('	HTTP check OK ('+str(resp.status)+')','okay')
					if(p.scheme=='http'):
						conn2 = httplib.HTTPConnection(p.netloc,timeout=20)
					else:
						conn2 = httplib.HTTPSConnection(p.netloc,context=ctx,timeout=20)
					conn2.request('GET', p.path)
					resp2 = conn2.getresponse()
					data = resp2.read()
					conn2.close();
					if(data.find(text)>0):
						print colourise('	Data check OK','okay')
					else:
						print colourise('	Data check error: '+url,'fail')
				else:
					if(resp.getheader('location','none')!='none'):
						resp.read();
						conn.close();
						checkUrl(resp.getheader('location','none'),text,False)
					else:
						print resp.getheaders()
						conn.close();
			else:
				print colourise('	HTTP check FAIL: '+str(resp.status)+' for '+url,'fail')
				conn.close();
		except (httplib.HTTPException, socket.error) as ex:
			print colourise('	Timeout check FAIL: '+url+' '+str(ex),'fail')
	else:
		print colourise('	DNS check FAIL: '+url,'fail')
	# return resp.status < 400 

with open('list.txt','r') as f:
	for line in f:
		if(line[:1]!='#' and len(line)>1):
			textLoc = line.find(' ')
			url = line[:textLoc];
			textcheck = line[textLoc+1:(len(line))].rstrip('\n')
			checkUrl(url,textcheck);