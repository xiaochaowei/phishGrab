from bs4 import BeautifulSoup
import urllib2
import MySQLdb
import gzip
from StringIO import StringIO
import sys
import datetime
conn = MySQLdb.connect(user = "root", passwd = "19920930", db = "PhishTank")
cursor = conn.cursor()
SELECTSQL = """ SELECT phish_id, DATE_FORMAT(submission_time ,"%Y-%m-%d") FROM phishSite WHERE phish_id = "{phish_id}" ; """
UPDATESQL = """ UPDATE phishSite SET expire_date = "{expire_date}", online = "no"; """

def extractDate(date_str):
	tmp = date_str.split(" ")
	date_format = """{month} {day} {year}"""
	return datetime.datetime.strptime(date_format.format(month = tmp[2], day = tmp[3][:-2], year = tmp[4]), "%b %d %Y").strftime("%Y-%m-%d")

def urlcrawl(url_prefix, url_surffix):
	url = url_prefix + url_surffix
	while(1):
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
				buf = StringIO(resp.read())
				f = gzip.GzipFile(fileobj = buf)
				source = f.read()
			else:
				source = resp.read()
			soup = BeautifulSoup(source,'html.parser')
			table = soup.table
			item = table.find_all('tr')
			for i in range(1,len(item)):
				ins = item[i].find_all('td')
				phish_id = ins[0].a.contents[0]
				submission_time = extractDate(ins[1].span.contents[0])
				#url = ins[1].contents[0]
				comment_sql = SELECTSQL.format(phish_id = phish_id)
				cursor.execute(comment_sql)
				rows = cursor.fetchall()
				if len(rows) >0:
			#		print rows[0][1] 
					if rows[0][1] > submission_time:
						print phish_id, url 
					comment_sql = UPDATESQL.format(expire_date = submission_time)
					cursor.execute(comment_sql)
					conn.commit()

			if soup.table.find_all('a')[-1].contents != [u'Older >']:
				return 
			next_page = soup.table.find_all('a')[-1]['href']
			#sys.stdout.write(next_page)
			url = url_prefix + next_page
	#		return urlcrawl(url_prefix, next_page)
		except urllib2.HTTPError as e:
			print "forbidden"
			time.sleep(10*60)
			return 		
		except urllib2.URLError as e:
			print "forbbiden"
			time.sleep(10*60)
			return 
		except Exception as e:
			print e
			#print sys.exc_info()
			return 
		# 	return False
url = "https://www.phishtank.com/phish_search.php"
surffix = "?valid=y&active=n&Search=Search"
urlcrawl(url, surffix)

