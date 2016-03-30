import sys
import requests
import MySQLdb
import urllib2
import thread
import time
import socket
import random
import gzip
import time
from StringIO import StringIO
from bs4 import BeautifulSoup

prefix_url = "http://www.phishtank.com/"

def run():
	conn = MySQLdb.connect(user = "root", passwd = "19920930", db = 'PhishTank')
	cursor = conn.cursor()
	QUERY_SQL = """ SELECT phish_id, phish_detail_url from phishSite where DATE_FORMAT(submission_time,"%Y") = "2015" """
	comment_sql = QUERY_SQL
	cursor.execute(comment_sql)
	rows = cursor.fetchall()
	floder_dir = "img/"
	for row in rows:
		url = row[1]
		phish_id = row[0]
		urlcrawl(floder_dir, phish_id, url)

def ungzip(data):		
	buf = StringIO(data)		
	f = gzip.GzipFile(fileobj = buf)
	source = f.read()
	return source
def urlcrawl(floder_dir,phish_id, url):
	try:
		req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',\
			'Accept':'text/html;q=0.9,*/*;q=0.8',\
			'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',\
			'Accept-Encoding':'gzip',\
			'Connection':'close',\
			'Referer':None }
		req_timeout = 10
		req = urllib2.Request(url, None, req_header)
		resp = urllib2.urlopen(req, None, req_timeout)
		if resp.headers.get('content-encoding') == "gzip":
			source = ungzip(resp.read())
		else:
			source = resp.read()
		soup = BeautifulSoup(source,'html')
		iframe = soup.find('iframe')
		suffix = iframe['src']
		image_url = prefix_url + suffix
		req = urllib2.Request(image_url, None, req_header)
		resp = urllib2.urlopen(req, None, req_timeout)
		if resp.headers.get('content-encoding') == "gzip":
			source = ungzip(resp.read())
		else:
			source = resp.read()
		soup = BeautifulSoup(source,'html')
		img_src = soup.img['src']
		print img_src
		data = urllib2.urlopen(img_src).read()
		fid = open(floder_dir+str(phish_id)+".jpg",'wb')
		fid.write(data)
		fid.close()
		sys.stdout.write("save success!\n")
	except:
		print sys.exc_info()
		return False
if __name__ == "__main__":
	run()
