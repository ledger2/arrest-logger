import requests
import configparser
from datetime import datetime, date, timedelta

root = "https://www8.iowa-city.org/icgov/apps/police/blotter.asp"
pushing = False
webhook = None

#Try to setup Discord webhook to push notifications
def tryDiscord():
	try:
		import DiscordHooks
		from DiscordHooks import Hook
	except ImportError:
		DiscordHooks = None 
	if DiscordHooks:
		print("Discord integration loading...")
		config = configparser.ConfigParser()
		URL = config["DiscordIntegration"]["WebhookURL"]
		if(URL != None):
			webhook = Hook(hook_url=URL)
			pushing = True
			print("Webhook setup complete")
		else:
			print("Webhook URL not supplied in 'config.ini'!")

#Fetch data on specified date (dateString MMDDYYYY)
def query(dateString):
	get = {"date":dateString}
	r = requests.get(root, params=get)
	if(r.status_code == 200):
		#Successful fetch, format and return data
 		return r.text
	else:
		print("Query failed. (Status: "+str(r.status_code)+"), URL: "+r.url)
		
def prettyPrintout(dict):
	#dictionary formatting: {"name": [offenseDatetime, dateOfBirth, arrestLocation, incidentNum, arrested, chargesList]}
	return None

tryDiscord()

dateToFetch = datetime.today()-timedelta(days=1)
newData = query(dateToFetch.strftime("%m%d%Y"))
print("Fetched...\n")
print(newData)