import os
import requests
import schedule
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test printing out an environment variable
#print("API Client ID:", os.getenv('BLIZZARD_CLIENT_ID'))

# Discord Alerts
def send_discord_alert(message):
    webhook_url = os.getenv('WEBHOOK_URL')
    print(f"Webhook URL: {webhook_url}")  # Debug print to check the URL
    if webhook_url is None:
        print("Webhook URL not found in environment variables.")
        return

    data = {"content": message, "username": "WoW Token Bot"}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print("Discord notification sent successfully!")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

#Threshold for alerts
BUY_THRESHOLD = 345000

def check_thresholds(price):
    if price >= BUY_THRESHOLD:
        #print(f"Sending Discord Alert...")
        message = f"@here: Good time to buy! Current price is {price} gold."
        send_discord_alert(message)
    else:
        print(f"No action needed. Current price is {price} gold.")

class BlizzardApiClient:
    def __init__(self):
        self.client_id = os.getenv('BLIZZARD_CLIENT_ID')
        self.client_secret = os.getenv('BLIZZARD_CLIENT_SECRET')
        self.access_token = self.get_oauth_token()

    def get_oauth_token(self):
        url = "https://us.battle.net/oauth/token"
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, data=data, auth=(self.client_id, self.client_secret))
        token_response = response.json()
        return token_response['access_token']

    def get_gold_price(self):
        url = f"https://us.api.blizzard.com/data/wow/token/?namespace=dynamic-us&locale=en_US&access_token={self.access_token}"
        response = requests.get(url)
        data = response.json()
        return int(data['price'] / 10000)

def job():
    api = BlizzardApiClient()
    token_price = api.get_gold_price()
    print(f"The current WoW token price in the USA is {token_price} gold!")
    check_thresholds(token_price)

# Schedule the job to run every hour
schedule.every().hour.do(job)

if __name__ == '__main__':
    # Run the job once at the start
    job()
    
    # Keep the script running and check the schedule
    while True:
        schedule.run_pending()
        time.sleep(1)