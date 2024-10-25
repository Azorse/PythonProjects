import os
import requests
import schedule
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the send_discord_alert function
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

# Define the BlizzardApiClient
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
        url = "https://us.api.blizzard.com/data/wow/token/?namespace=dynamic-us&locale=en_US"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return int(data['price'] / 10000)

# Define threshold checks and scheduling
def check_thresholds(price):
    if price >= 350000:
        message = f"@here: Time to Buy, Current price is {price} gold."
        send_discord_alert(message)
    elif price <= 150000:
        message = f"@here: Time to Sell, Current price is {price} gold."
        send_discord_alert(message)
    else:
        print(f"No actions taken")

def job():
    api = BlizzardApiClient()
    token_price = api.get_gold_price()
    print(f"The current WoW token price is {token_price} gold.")
    check_thresholds(token_price)

# Schedule the job to run every hour
schedule.every().hour.do(job)

if __name__ == '__main__':
    job() 
    while True:
        schedule.run_pending()
        time.sleep(1)

