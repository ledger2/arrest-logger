import urllib3
from datetime import datetime

root = "https://www8.iowa-city.org/icgov/apps/police/blotter.asp?date="

def query(dateString):
	url = root+dateString
	http = urllib3.PoolManager()
	r = http.request("GET", url)
	if(r.status == 200):
		return r.data
	else:
		print("Query failed. (Status: "+str(r.status)+")")

pageData = query(str(datetime.now().month)+str(datetime.now().day-1)+str(datetime.now().year))

print("Fetch successful...\n")
print(pageData)