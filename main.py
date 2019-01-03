import requests
import configparser
import sqlite3
from datetime import datetime, date, timedelta

root = "https://www8.iowa-city.org/icgov/apps/police/blotter.asp"
findText = "<strong>Charge(s)</strong>" #String used to strip most of the raw HTML down and locate table

pushing = False
storing = False
webhook = None
config = configparser.ConfigParser()


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
	if(config["General"]["UsingDatabase"] == yes):
		try:
			dbConnection = sqlite3.connect("arrests.db")
			db = dbConnection.cursor()
			storing = True
			db.execute("CREATE TABLE IF NOT EXISTS arrests(incident INTEGER PRIMARY KEY, name TEXT, birthday TEXT, incidentTime TEXT, location TEXT, arrested BOOLEAN, charges TEXT) WITHOUT ROWID;")
			db.execute("CREATE TABLE IF NOT EXISTS datesFetched(date TEXT, fetched TEXT) WITHOUT ROWID;")
			db.commit()
	tryDiscord()


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
		next = raw[next:].find("<!--")+next #find new arrest
		if(next != -1):
			for i in elements:
				next = raw[next:].find(i)+len(i)+next
				end = raw[next:].find("</span>")+next
				if(i == elements[5]):								#special routine for grabbing ID
					case = raw[next:end]
				elif(i == elements[7]):								#special clean routine for charges
					storing = raw[next:end].replace("<br/>"," // ")
					if(storing[len(storing)-1] == " "): 			#clean ending
						storing = storing[:len(storing)-1]
					toStore.append(storing)
				else:
					storing = raw[next:end]
					if(storing[len(storing)-1] == " "):				#clean ending
						storing = storing[:len(storing)-1]
					toStore.append(storing)
			results[case] = toStore
		else:
			break
		break
	print("Query stripped")
	return results

#Fetch data on specified date (dateString MMDDYYYY)
def query(dateString):
	get = {"date":dateString}
	r = requests.get(root, params=get)
	if(r.status_code == 200):
		#Successful fetch, format and return data
 		#return r.text
		start = r.text.find(findText)+len(findText)
		print("HTML query received")
		return stripTable(r.text[start:])
	else:
		print("HTML query failed. (Status: "+str(r.status_code)+"), URL: "+r.url)

		
def prettyPrintout(dict):
	#dictionary formatting: {incident: [name, dateOfBirth, offenseDatetime, arrestLocation, incidentNum, arrested, chargesList]}
	return None

	
setup()

dateToFetch = datetime.today()-timedelta(days=1)
newData = query(dateToFetch.strftime("%m%d%Y"))
print("Fetched...\n")
print(newData)