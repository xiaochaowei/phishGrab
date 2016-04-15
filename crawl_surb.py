from selenium import webdriver
import MySQLdb
import time
import datetime 
import thread
import socket
import sys
import os
import requests
# PREFIX = "/raid/reputation/merit/raw/" + today +""
driver = webdriver.PhantomJS(executable_path = "./phantomjs") 
conn = MySQLdb.connect(user = "root", passwd = "19920930", db = "PhishSurbl")
cursor = conn.cursor()
SELECT_URL = """ SELECT phish_id, url FROM phishSite where DATE_FORMAT(submission_time ,"%Y-%m-%d") = "{submission_time}" AND grab = 0; """
UPDATE_URL = """ UPDATE phishSite SET grab = {grab}, ip = "{ip}" WHERE phish_id={phish_id} ;"""
mylock = thread.allocate_lock()
# invaild_str = "<html><head></head><body></body></html>"
# from selenium import webdriver

#first, extact PH data
#then map the IP address 
#grab 

def getUrl(filename):
	url2IP = {}
	fid = open(filename,'r')
	str_tmp = fid.read()
	str_list = str_tmp.split('\n')
	for i in range(2,len(str_list)):
		tmp = str_list[i].split('|')
		url_name = tmp[0]
		ip_addr = tmp[0]

		if url_name not in url2IP:
			url2IP[url_name] = []
			url2IP[url_name].append(ip_addr)
		else:
			url2IP[url_name].append(ip_addr)
	return url2IP

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
			time.sleep(60)
		for row in rows:
			sys.stdout.flush()
			url = row[1]
			phish_id = row[0]
			try:
				ip = socket.gethostbyname(url)
				sys.stdout.write("success solve: " + url+ "\n")
				url_abs = "http://" + url
				print url_abs
				r = requests.get(url_abs, timeout = 10)
				if not r.status_code == 200:
					sys.stdout.write("status_code not 200" + row[1] + "\n")
					mylock.acquire()
					comment_sql = UPDATE_URL.format(grab = -3, phish_id = row[0], ip = ip)
					cursor.execute(comment_sql)
					conn.commit()
					mylock.release()
					continue
				if urlcrawlDriver(floder_dir, phish_id,url):
					# print "success"
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
			except Exception, e:
				print e
				sys.stdout.write("solve ip failed," + row[1] + "\n")
				mylock.acquire()
				comment_sql = UPDATE_URL.format(grab = -1, phish_id = row[0], ip = "")
				cursor.execute(comment_sql)
				conn.commit()
				mylock.release()



def urlcrawlDriver(floder_dir, phish_id, url):
	url_abs = "http://www." + url
	try:
		print "start to save file"
		driver.get(url_abs)
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

# def urlcrawlDriver(flod):
# 	url_abs = "http://www." + url
# 	try:
# 		driver.get(url_abs)
# 		if driver.page_source == invaild_str:
# 			print "invaild",driver.current_url
# 		elif driver.find_element_by_xpath("//title").get_attribute('innerHTML') == "404 Not Found":
# 				print driver.current_url
# 		else:
# 			savePage(url, driver.page_source, save_path)
# 			driver.save_screenshot(save_path + url + 'jpg')
# 	except:
# 		print "crawl error"

def grabSurbl(filename):
	fid = open(filename, 'r')
	tmp = fid.read()
	data_list = tmp.split('\n')
	bais = 7
	list_len = len(data_list)
	mylock.acquire()
	for i in range(bais, list_len):
		str_tmp = data_list[i]
		if str_tmp.find('[ph]') != -1:
			url_sub = str_tmp[:str_tmp.find(' ')]
			saveToDB(url_sub)
	conn.commit()
	mylock.release()
	return

def saveToDB(url):
	INSERT_SQL = """ INSERT INTO PhishSite(url) VALUES ("{url}") ; """
	comment_sql = INSERT_SQL.format(url = url)
	print url
	cursor.execute(comment_sql)

def getUrlList():
	while(1):
		print "sacn url list: "
		today = datetime.date.today().strftime("%Y%m%d")
		sys.stdout.write("garb data at " + today + "\n")
		# prefix_floder = "/raid/reputation/merit/raw/" + today +""
		prefix_floder = today
		if not (os.path.isfile(prefix_floder + "/multi.surbl.org.resolved") and os.path.isfile(prefix_floder + "/multi.surbl.org.rbldnsd")):
			time.sleep(60 * 60)
		else:
			print "exists"
			grabSurbl(prefix_floder + "/multi.surbl.org.rbldnsd")
		tomorrow = datetime.date.today() + datetime.timedelta(days = 1)
		left_time = datetime.datetime.combine(tomorrow, datetime.time(0,0)) - datetime.datetime.now()
		time.sleep(left_time.seconds)
# run()
if __name__  == "__main__":
	thread.start_new_thread(updateUrlList,())
	while (1):
		# updateUrlList()
		getUrlList()
		pass
