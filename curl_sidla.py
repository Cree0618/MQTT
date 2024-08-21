import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re

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
            st.success("Cookie refreshed successfully")
        else:
            st.error(f"Failed to refresh cookie. Status code: {response.status_code}")

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
                st.warning("Unauthorized. Refreshing cookie and retrying...")
                self.refresh_cookie()
            else:
                st.warning(f"Error: {response.status_code}. Retrying in 5 seconds...")
                time.sleep(5)

        st.error(f"Failed to get data after {max_retries} attempts")
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

@st.cache_data
def fetch_data(api, payloads):
    all_subjects = []
    for payload in payloads:
        address = format_address(payload)
        result = api.search_subjects(payload)
        if result:
            subjects = extract_subject_data(result, address)
            all_subjects.extend(subjects)
            st.write(f"Found {len(subjects)} subjects for address {address}")
        else:
            st.write(f"No data retrieved for address {address}")
        time.sleep(1)
    return pd.DataFrame(all_subjects)

def main():
    st.title("ARES API Data Comparison")

    uploaded_file = st.file_uploader("Choose a CSV file to replace the original", type="csv")

    if uploaded_file is not None:
        original_df = pd.read_csv(uploaded_file, delimiter=';')
        st.success("File successfully uploaded and processed!")
    else:
        st.warning("Please upload a CSV file to proceed.")
        return

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
    ]

     if 'df_ares' not in st.session_state:
        st.session_state.df_ares = None

    if st.button("Fetch and Compare Data"):
        with st.spinner("Fetching data from API..."):
            st.session_state.df_ares = fetch_data(api, payloads)
        
        st.success("Data fetched successfully!")

    if st.session_state.df_ares is not None:
        df_ares = st.session_state.df_ares
        
        # Data processing
        original_df_modified = original_df.copy()
        original_df_modified['IČO'] = original_df_modified['IČO'].astype(str).str.strip().str.zfill(8)
        original_df_modified['Název'] = original_df_modified['Název'].str.replace('"', '')

        df_ares_modified = df_ares.copy()
        df_ares_modified['IČO'] = df_ares_modified['IČO'].astype(str).str.strip().str.zfill(8)
        df_ares_modified['Name'] = df_ares_modified['Name'].str.replace('"', '')

        ico_in_api_not_in_csv = df_ares_modified[~df_ares_modified['IČO'].isin(original_df_modified['IČO'])]
        ico_in_api_not_in_csv = ico_in_api_not_in_csv[['IČO', 'Name']]

        # Display results
        st.subheader("Results")
        st.write(f"Total IČO numbers in original CSV: {len(original_df_modified)}")
        st.write(f"Total IČO numbers in API data: {len(df_ares_modified)}")
        st.write(f"IČO numbers in API but not in original CSV: {len(ico_in_api_not_in_csv)}")

        st.subheader("Examples of IČO numbers in API but not in original CSV:")
        st.dataframe(ico_in_api_not_in_csv.head())

        # Option to download results
        csv_ico_diff = ico_in_api_not_in_csv.to_csv(index=False)
        st.download_button(
            label="Download IČO differences as CSV",
            data=csv_ico_diff,
            file_name="ico_in_api_not_in_original_csv.csv",
            mime="text/csv",
        )

        # New download button for df_ares_modified
        csv_ares_modified = df_ares_modified.to_csv(index=False)
        st.download_button(
            label="Download all API data as CSV",
            data=csv_ares_modified,
            file_name="ares_api_data.csv",
            mime="text/csv",
        )

    st.write("Created by KZ 2024")

if __name__ == "__main__":
    main()
#writet text to the app saying "Vytvořeno KZ 2024"

st.text("Vytvořeno KZ 2024")
if __name__ == "__main__":
    main()