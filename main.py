import urllib3
import configparser
from datetime import datetime

root = "https://www8.iowa-city.org/icgov/apps/police/blotter.asp?date="

def tryDiscord():
	try:
		import requests
		import discord
		from discord import Webhook, RequestsWebhookAdapter, File
	except ImportError:
		requests = None
		discord = None 
	if requests && discord:
		print("Discord integration loading...")
		config = configparser.ConfigParser()
		URL = config["DiscordIntegration"]["WebhookURL"]
		hook = Webhook.from_url(URL, adapter=RequestsWebhookAdapter())
		print("Webhook setup complete")
	
def query(dateString):
	url = root+dateString
	http = urllib3.PoolManager()
	r = http.request("GET", url)
	if(r.status == 200):
		return r.data
	else:
		print("Query failed. (Status: "+str(r.status)+")")

tryDiscord()

pageData = query(str(datetime.now().month)+str(datetime.now().day-1)+str(datetime.now().year))
print("Fetched...\n")
print(pageData)