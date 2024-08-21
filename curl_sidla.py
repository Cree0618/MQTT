import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class AresAPI:
    def __init__(self):
        self.base_url = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat"
        self.session = requests.Session()
        self.cookie = None
        self.cookie_expiry = None

    def refresh_cookie(self):
        response = self.session.get("https://ares.gov.cz/ekonomicke-subjekty")
        if response.status_code == 200:
            self.cookie = self.session.cookies.get("GN-TOKEN-CSP")
            self.cookie_expiry = datetime.now() + timedelta(hours=1)
            print("Cookie refreshed successfully")
        else:
            print(f"Failed to refresh cookie. Status code: {response.status_code}")

    def check_cookie(self):
        if not self.cookie or (self.cookie_expiry and datetime.now() > self.cookie_expiry):
            self.refresh_cookie()

    def search_subjects(self, payload):
        self.check_cookie()
        headers = {
            "Host": "ares.gov.cz",
            "Cookie": f"GN-TOKEN-CSP={self.cookie}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://ares.gov.cz",
            "Referer": "https://ares.gov.cz/ekonomicke-subjekty"
        }

        max_retries = 3
        for attempt in range(max_retries):
            response = self.session.post(self.base_url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("Unauthorized. Refreshing cookie and retrying...")
                self.refresh_cookie()
            else:
                print(f"Error: {response.status_code}. Retrying in 5 seconds...")
                import time
                time.sleep(5)

        print(f"Failed to get data after {max_retries} attempts")
        return None

def extract_subject_data(result, address):
    subjects = result.get('ekonomickeSubjekty', [])
    return [{'Name': subject.get('obchodniJmeno', ''), 
             'IČO': subject.get('ico', ''),
             'Address': address} for subject in subjects]

def format_address(payload):
    sidlo = payload['sidlo']
    address = f"{sidlo['cisloDomovni']}"
    if 'cisloOrientacni' in sidlo:
        address += f"/{sidlo['cisloOrientacni']}"
    if 'cisloOrientacniPismeno' in sidlo:
        address += sidlo['cisloOrientacniPismeno']
    return address

api = AresAPI()

payloads = [
    {"sidlo":{"cisloDomovni":1442,"cisloOrientacni":1,"cisloOrientacniPismeno":"b","kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":478652},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1422,"cisloOrientacni":1,"cisloOrientacniPismeno":"a","kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":478652},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1138,"cisloOrientacni":1,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":449661},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1552,"cisloOrientacni":58,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":456225},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1525,"cisloOrientacni":1,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":717592},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1461,"cisloOrientacni":2,"cisloOrientacniPismeno":"a","kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":478652},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1481,"cisloOrientacni":4,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":478652},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1559,"cisloOrientacni":5,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":730700},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1561,"cisloOrientacni":4,"cisloOrientacniPismeno":"a","kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":478652},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1448,"cisloOrientacni":7,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":717592},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1449,"cisloOrientacni":9,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":717592},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":1100,"cisloOrientacni":2,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":478652},"pocet":200,"start":0,"razeni":[]},
    {"sidlo":{"cisloDomovni":266,"cisloOrientacni":2,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":730700},"pocet":200,"start":0,"razeni":[]}
    
    # New payload added here
]

all_subjects = []

for payload in payloads:
    address = format_address(payload)
    result = api.search_subjects(payload)
    if result:
        subjects = extract_subject_data(result, address)
        all_subjects.extend(subjects)
        print(f"Found {len(subjects)} subjects for address {address}")
    else:
        print(f"No data retrieved for address {address}")
    time.sleep(1)  # Add a 5-second delay between requests

df = pd.DataFrame(all_subjects)
print(df)

# Save to CSV
df.to_csv('subjects_data.csv', index=False)
print("Data saved to subjects_data.csv")