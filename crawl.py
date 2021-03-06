import sys
import time 
import os
import datetime
# invaild_str = "<html><head></head><body></body></html>"
from selenium import webdriver
import requests
import MySQLdb
import urllib2
import re
import thread
import time
import socket
import random
import gzip
from StringIO import StringIO

driver = webdriver.PhantomJS(executable_path = "./phantomjs") 
API_KEYS = [\
"7ceda52f14d52c6ed8ba56f45b2e7587fc423d467e7335d11473e1a795897d2c",\
"4e302260ddab4da32760226c56e1a00e8f7e0a25a1f96f8bbf7e85ce81e67f1e",\
"58aceeaa41b895814baf85b090d4cefbd69e7476d7895b7a91e9f14507afa7b2",\
"2fd76c8e95730c81cc268617e1bd4019dd8322460f71e39212796299c8881d30",\
"8cbcdc7f55877fbdaa60d15699191fc6af643e26718b8e41a448b77527e5b676",\
"09840bf19fcdf63cf067f6d44901f8e3a9150b3f7f6b4c2e15f783378e3d4392",\
"18d21fd5bc97c6bbed8ace352dc2d56f5649d0593987a7dfd46104648c70a889",\
"4f335cafd18bcc206388e68272387c0815063197cbc66e74694301e96aa06587",\
"241e183a0417770d4eaee3d075d47797821caa06079562294c9f7e5b01426fb3",\
"0eecf933acf72a6423bf79c8765afe9fe717788514dcecb918ac025518f693bb",\
"3420f3c862e0b99ab1c3b7babb0c1a1f2bc5efabe0916037f42f712bfa17465c"]

API_KEY = "7ceda52f14d52c6ed8ba56f45b2e7587fc423d467e7335d11473e1a795897d2c"
conn = MySQLdb.connect(user = "root", passwd = "19920930", db = 'PhishTank')
cursor = conn.cursor()
INSERT_SQL = """ INSERT INTO phishSite(phish_id, url, phish_detail_url, \
	submission_time, verified, verification_time, online, target) VALUES \
	 ( {phish_id},"{url}", "{phish_detail_url}", \
	"{submission_time}", "{verified}", "{verification_time}", "{online}", \
	"{target}"); """
SELECT_URL = """SELECT phish_id, url  FROM phishSite where submission_time = "{submission_time}" AND verified = "yes" AND grab = 0; """
UPDATE_URL = """ UPDATE phishSite SET grab = {grab}, ip = "{ip}" WHERE phish_id={phish_id} ;"""
time_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
mylock = thread.allocate_lock()

def verifyExpire():
	today = datetime.date.today().strftime("%Y-%m-%d")
	VERIFY_SQL = """SELECT url,phish_id from phishSite where grab=1 and online = 'yes' ; """
	SET_EXPIRE_SQL = """ UPDATE phishSite SET expire_date ="{expire_time}", online='no' where phish_id = {phish_id}; """
	comment_sql = VERIFY_SQL
	mylock.acquire()
	cursor.execute (comment_sql)
	rows = cursor.fetchall()
	mylock.release()
	for row in rows:
		url = row[0]
		url = url[url.find('//'):]
		phish_id = row[1]	
		try:
			ip = socket.gethostbyname(url[:url.find('/')])
		except:
			mylock.acquire()
			comment_sql = SET_EXPIRE_SQL.format(expire_date = today,phish_id = phish_id)
			cursor.execute(comment_sql)
			conn.commit()
			mylock.release()
	time.sleep(60*60*8)
 
def saveNewData(data, max_store):
		data_list = data.split('\n')
		data_len = len(data_list)
		for i in range(1,data_len):
			p = data_list[i].split(',')#phish_instance 
			p = instanceClear(p)
			if p == None:
				print i, " and ", data_len
				print "here"
				continue
			if int(p[0]) > int(max_store):
				print "insert ",p[0], "max score: ", max_store
				comment_sql = INSERT_SQL.format(\
					phish_id = p[0],\
					url = p[1],\
					phish_detail_url = p[2],\
					submission_time = p[3].split('T')[0],\
					verified = p[4],\
					verification_time = p[5].split('T')[0],\
					online = p[6],\
					target = p[7])
				cursor.execute(comment_sql)
			else:
				print p[0]
				break
		conn.commit()

def instanceClear(ins):
	new_ins = []
	try:
		if not (time_pattern.match(ins[3].split('T')[0]) and time_pattern.match(ins[5].split('T')[0])):
			print "time error"
			return None
		ins[1] = ins[1].encode('utf-8')
		for item in ins:
			item = item.replace('"',"")
			item = item.replace("'",r"\'")
			new_ins.append(item)
		return new_ins
	except:
		print "data wrong"
		return None

# def grabDataFromPhishTank():
# 	prefix_floder = datetime.date.today(),strftime("%Y%m%d")
# 	prefix_floder = prefix_floder + "_phishTank"
# 	if not os.path.exists(prefix_floder):
# 		print "mkdir ", prefix_floder
# 		os.mkdir(prefix_floder)
# 	prefix_floder = prefix_floder  +  "/"
# 	grabPhishtank()

def grabPhishtank():
	global API_KEY
	global API_KEYS
	#TIME DIFFERENT NEED TO CONSDIER 
	url = "http://data.phishtank.com/data/"+API_KEY+"/online-valid.csv"
	sys.stdout.write("get data from PhishTank!")
	r = requests.post(url)
	print r.status_code
	if r.status_code == 200:
		comment_sql = "SELECT distinct max(phish_id) from phishSite"
		cursor.execute(comment_sql)
		max_store = cursor.fetchone()[0]
		if max_store == None:
			max_store = 0
		saveNewData(r.text, max_store)
		time.sleep(60 * 60)
	else:
		API_KEY = API_KEYS[random.randrange(0,len(API_KEYS))]
		time.sleep(60)

# only for test
	# fid = open("result.txt","r")
	# data = fid.read()
	# fid.close()
	# comment_sql = "SELECT distinct max(phish_id) from phishSite ;"
	# mylock.acquire()
	# cursor.execute(comment_sql)
	# max_store = cursor.fetchone()[0]
	# mylock.release()
	# saveNewData(data, max_store)
def updateUrlList():
	while 1:
		today = datetime.date.today().strftime("%Y-%m-%d")
		sys.stdout.write("garb data at " + today + "\n")
		floder_dir = "phish_data/" + today + "/"
		if not os.path.exists(floder_dir):
			os.mkdir(floder_dir)
			print "mkdir success!"
		mylock.acquire()
		comment_sql = SELECT_URL.format(submission_time = today)
		cursor.execute(comment_sql)
		rows = cursor.fetchall()
		mylock.release()
		if len(rows) == 0:
			sys.stdout.write("queue vacant, wait for a minutes!\n")
			time.sleep(10*60)
		for row in rows:
			sys.stdout.flush()
			url_tmp = row[1][row[1].find("//")+2:]
			try:
				ip = socket.gethostbyname(url_tmp[:url_tmp.find('/')])
				sys.stdout.write("success solve: " + url_tmp[:url_tmp.find('/')] + "\n")
				phish_id = row[0]
				url = row[1]
				r = requests.get(url, timeout = 10)
				if not r.status_code == 200:
					sys.stdout.write("status_code not 200" + row[1] + "\n")
					mylock.acquire()
					comment_sql = UPDATE_URL.format(grab = -3, phish_id = row[0], ip = "")
					cursor.execute(comment_sql)
					conn.commit()
					mylock.release()
					continue
				if urlcrawlDriver(floder_dir, phish_id, url):
					comment_sql = UPDATE_URL.format(grab = 1, phish_id = phish_id, ip = ip)
					mylock.acquire()
					cursor.execute(comment_sql)
					conn.commit()
					mylock.release()
				else:
					sys.stdout.write("grab html failed," + row[1] + "\n")
					mylock.acquire()
					comment_sql = UPDATE_URL.format(grab = -2, phish_id = row[0], ip = "")
					cursor.execute(comment_sql)
					conn.commit()
					mylock.release()
			except:
				sys.stdout.write("solve ip failed," + row[1] + "\n")
				mylock.acquire()
				comment_sql = UPDATE_URL.format(grab = -1, phish_id = row[0], ip = "")
				cursor.execute(comment_sql)
				conn.commit()
				mylock.release()

def urlcrawl(floder_dir, phish_id,  url):
	try:
		req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',\
			'Accept':'text/html;q=0.9,*/*;q=0.8',\
			'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',\
			'Accept-Encoding':'gzip',\
			'Connection':'close',\
			'Referer':None }
		req_timeout = 5
		req = urllib2.Request(url, None, req_header)
		resp = urllib2.urlopen(req, None, req_timeout)
		if resp.headers.get('content-encoding') == "gzip":
			print url
			buf = StringIO(resp.read())
			f = gzip.GzipFile(fileobj = buf)
			source = f.read()
		else:
			source = resp.read()
		savePage(floder_dir, str(phish_id), source)
		return True
	except:
		print sys.exc_info()
		return False

def urlcrawlDriver(floder_dir, phish_id, url):
	try:
		driver.get(url)
		source = driver.page_source
		savePage(floder_dir, str(phish_id), source.encode('utf-8'))
		sys.stdout.write("save successfull\n")
		return True
	except:
		sys.stdout.write("save failed\n")
		sys.stdout.write(sys.exc_info())
		return False

def savePage(save_path, file_name, content):
	try:
		full_filename = save_path + file_name + ".html"
		fid = open(full_filename, 'w')
		fid.write(content)
		fid.close()
		driver.save_screenshot(full_filename[:-5] + ".jpg")
	except:
		sys.stdout.write(sys.exc_info()+"\n")

if __name__ == "__main__":
	thread.start_new_thread(updateUrlList,())
	thread.start_new_thread(verifyExpire,())
	while(1):
		grabPhishtank()
		pass
