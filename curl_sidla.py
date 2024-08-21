import requests
import pandas as pd
import time
from datetime import datetime, timedelta

class AresAPI:
    def __init__(self):
        self.base_url = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat"
        self.session = requests.Session()
        self.cookie = None
        self.cookie_expiry = None

    def refresh_cookie(self):
        """Refresh the cookie by making a request to the main page"""
        response = self.session.get("https://ares.gov.cz/ekonomicke-subjekty")
        if response.status_code == 200:
            self.cookie = self.session.cookies.get("GN-TOKEN-CSP")
            self.cookie_expiry = datetime.now() + timedelta(hours=1)  # Assume 1-hour expiry
            print("Cookie refreshed successfully")
        else:
            print(f"Failed to refresh cookie. Status code: {response.status_code}")

    def check_cookie(self):
        """Check if the cookie is valid, refresh if necessary"""
        if not self.cookie or (self.cookie_expiry and datetime.now() > self.cookie_expiry):
            self.refresh_cookie()

    def search_subjects(self, payload):
        """Search for economic subjects"""
        self.check_cookie()

        headers = {
            "Host": "ares.gov.cz",
            "Cookie": f"GN-TOKEN-CSP={self.cookie}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36",
            "Origin": "https://ares.gov.cz",
            "Referer": "https://ares.gov.cz/ekonomicke-subjekty"
        }

        max_retries = 3
        for attempt in range(max_retries):
            response = self.session.post(self.base_url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:  # Unauthorized, possibly due to expired cookie
                print("Unauthorized. Refreshing cookie and retrying...")
                self.refresh_cookie()
            else:
                print(f"Error: {response.status_code}. Retrying in 5 seconds...")
                time.sleep(5)

        print(f"Failed to get data after {max_retries} attempts")
        return None

def create_dataframe(data):
    """Create a pandas DataFrame from the API response"""
    subjects = data.get('ekonomickeSubjekty', [])
    subject_data = [{'Name': subject.get('obchodniJmeno', ''), 'IČO': subject.get('ico', '')} for subject in subjects]
    return pd.DataFrame(subject_data)

# Usage
api = AresAPI()

payload = {
    "sidlo": {
        "cisloDomovni": 1525,
        "cisloOrientacni": 1,
        "kodObce": 554782,
        "kodMestskeCastiObvodu": 500119,
        "kodUlice": 717592
    },
    "pocet": 200,
    "start": 0,
    "razeni": []
}

data = api.search_subjects(payload)
if data:
    df = create_dataframe(data)
    print(df)
else:
    print("Failed to retrieve data")