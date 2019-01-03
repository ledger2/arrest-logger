import requests
import configparser
import sqlite3
from datetime import datetime, date, timedelta

root = "https://www8.iowa-city.org/icgov/apps/police/blotter.asp"
findText = "<strong>Charge(s)</strong>" #String used to strip most of the raw HTML down and locate table

pushing = False
useDB = False
webhook = None
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


#Try to setup Discord webhook to push notifications
def tryDiscord():
	try:
		import DiscordHooks
		from DiscordHooks import Hook
	except ImportError:
		DiscordHooks = None 
	if DiscordHooks:
		print("Discord integration loading...")
		try:
			URL = config["DiscordIntegration"]["WebhookURL"]
			webhook = Hook(hook_url=URL)
			pushing = True
			print("Webhook setup complete")
		except:
			print("Webhook URL not supplied in 'config.ini'!")


def setup():
	if(config["General"]["UsingDatabase"] == "yes"):
		dbConnection = sqlite3.connect("arrests.db")
		db = dbConnection.cursor()
		useDB = True
		db.execute("CREATE TABLE IF NOT EXISTS arrests(incident INTEGER PRIMARY KEY, name TEXT, address TEXT, birthday TEXT, offenseDate TEXT, location TEXT, arrested TEXT, charges TEXT, UNIQUE(incident)) WITHOUT ROWID;")
		db.execute("CREATE TABLE IF NOT EXISTS datesFetched(date TEXT PRIMARY KEY, fetched TEXT, UNIQUE(date)) WITHOUT ROWID;")
		dbConnection.commit()
	else:
		print("Not using local DB!")
	tryDiscord()
	

#store the data and mark date as fetched
def logData(transfer, dateFetched):
	dbConnection = sqlite3.connect("arrests.db")
	db = dbConnection.cursor()
	for i in transfer:
		db.execute("INSERT OR IGNORE INTO arrests(incident,name,address,birthday,offenseDate,location,arrested,charges) VALUES("
					+str(i[0])+","+str(i[1])+","+str(i[2])+","+str(i[3])+","+str(i[4])+","+str(i[5])+","+str(i[6])+","+str(i[7])+");")
	db.execute("INSERT OR IGNORE INTO datesFetched(date,fetched) VALUES("
				+dateFetched+","+datetime.today()+");")
	dbConnection.commit()
					

#take trimmed HTML and return results. Should return empty dictionary if no results
def stripTable(raw):
	elements = ["<span>name - ",
				"<span>address - ",
				"<span>DateOfBirth - ",
				"<span>OffenseDate - ",
				"<span>location - ",
				"<span>CaseNumber - ",		#special: primary key (index 5)
				"<span>jailed - ",
				"<span>Charges - "]			#special: replace <br> with dividers
	results = {}
	next = 0
	while True:
		case = 0
		toStore = []
		toNext = raw[next:].find("<!--")
		if(toNext != -1):						#Verify there actually is a next...
			next = toNext+next					#...and set it up
			for i in elements:
				next = raw[next:].find(i)+len(i)+next
				end = raw[next:].find("</span>")+next
				if(i == elements[5]):								#special routine for grabbing ID
					case = raw[next:end]
				elif(i == elements[7]):								#special clean routine for charges
					if(storing[len(storing)-1] == " "): 			#clean ending
						storing = storing[:len(storing)-1]
					storing = raw[next:end].replace("<br/>"," // ")
					toStore.append(storing)
				else:
					storing = raw[next:end]
					if(len(storing) > 0):						#empty fields need to be filtered out
						if(storing[len(storing)-1] == " "):			#clean ending
							storing = storing[:len(storing)-1]
					toStore.append(storing)
			results[case] = toStore
		else:
			break
	print("Query stripped")
	return results
	

#Fetch data on specified date (dateString MMDDYYYY)
def query(dateString):
	print("Querying "+dateString)
	get = {"date":dateString}
	r = requests.get(root, params=get)
	if(r.status_code == 200):
		#Successful fetch, format and return data
 		#return r.text
		start = r.text.find(findText)+len(findText)
		print("HTML query received")
		return stripTable(r.text[start:])
	else:
		print("HTML query failed. (Status: "+str(r.status_code)+", URL: "+r.url+")")

		
def prettyPrintout(dict):
	#dictionary formatting
	return None

	
setup()

dateToFetch = (datetime.today()-timedelta(days=1)).strftime("%m%d%Y")
newData = query(dateToFetch)
print("Fetched...\n")
print(newData)
logData(newData,dateToFetch)