import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re
import bcrypt
import openpyxl

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
            st.success("Cookie úspěšně obnoven")
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


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if bcrypt.checkpw(st.session_state["password"].encode(), st.secrets["hashed_password"].encode()):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True



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


def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file, delimiter=';')
    elif file.name.endswith(('.xlsx', '.xls')):
        original_excel = openpyxl.load_workbook(file)
        sheet = original_excel.active
        data = sheet.values
        cols = next(data)[0:]
        data = list(data)
        df = pd.DataFrame(data, columns=cols)
        df_modified = df.drop([0,1,2,3,4,5])
        # set row 6 as column names
        df_modified.columns = df_modified.iloc[0]
        df_modified = df_modified.drop([6])
        df_modified = df_modified[['Budova', 'IČO', 'Název', 'adresa']]
        
        # Convert all columns to string type to avoid mixed data types
        df_modified = df_modified.astype(str)
        
        # Remove any leading/trailing whitespace
        df_modified = df_modified.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        return df_modified
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None

def main():
    
    st.title("Kontrola firemních sídel na PST budovách dle Aresu a porovnání s posledním stavem")

    uploaded_file = st.file_uploader("Vyberte CSV nebo Excel soubor k porovnání", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        original_df = load_data(uploaded_file)
        if original_df is not None:
            st.success("Soubor úspěšně nahrán a zpracován!")
        else:
            return
    else:
        st.warning("Prosím nahrajte CSV nebo Excel soubor pro porovnání")
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
        {"sidlo":{"cisloDomovni":266,"cisloOrientacni":2,"kodObce":554782,"kodMestskeCastiObvodu":500119,"kodUlice":730700},"pocet":200,"start":0,"razeni":[]},
        {"sidlo":{"cisloDomovni":2427,"cisloOrientacni":2,"kodObce":554782,"kodMestskeCastiObvodu":547034,"kodUlice":504106},"pocet":200,"start":0,"razeni":[]}
    ]

    if st.button("Vyčíst data z Aresu a porovnat s nahraným souborem"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        all_subjects = []

        for i, payload in enumerate(payloads):
            address = format_address(payload)
            status_text.text(f"Získávám data z Aresu pro adresu {address}...")
            result = api.search_subjects(payload)
            if result:
                subjects = extract_subject_data(result, address)
                all_subjects.extend(subjects)
                st.write(f"Nalezeno {len(subjects)} subjektu na adrese {address}")
            else:
                st.write(f"Žádná data nenalezena pro adresu {address}")
            progress_bar.progress((i + 1) / len(payloads))

        df_ares = pd.DataFrame(all_subjects)

        # Data processing
        # Remove leading and trailing whitespaces from IČO and fill with zeros
        original_df_modified = original_df.copy()
        original_df_modified['IČO'] = original_df_modified['IČO'].astype(str).str.strip().str.zfill(8)
        original_df_modified['Název'] = original_df_modified['Název'].str.replace('"', '')

        df_ares_modified = df_ares.copy()
        df_ares_modified['IČO'] = df_ares_modified['IČO'].astype(str).str.strip().str.zfill(8)
        df_ares_modified['Name'] = df_ares_modified['Name'].str.replace('"', '')

        ico_in_api_not_in_csv = df_ares_modified[~df_ares_modified['IČO'].isin(original_df_modified['IČO'])]
        ico_in_original_not_in_api = original_df_modified[~original_df_modified['IČO'].isin(df_ares_modified['IČO'])]
        ico_in_original_not_in_api = ico_in_original_not_in_api[['IČO', 'Název']]
        ico_in_api_not_in_csv = ico_in_api_not_in_csv[['IČO', 'Name']]

        # Display results
        st.subheader(":green[Výsledky]")
        st.write(f"CELKEM IČO v originálním souboru: {len(original_df_modified)}")
        st.write(f"Celkem IČO v datech z Aresu: {len(df_ares_modified)}")
        st.write(f":blue[IČO nalezené v Aresu] ale NE v posledním souboru (pravděpodovně nové sídlo): {len(ico_in_api_not_in_csv)}")
        st.write(f":red[IČO nenalezené v Aresu] (pravděpodobně zrušeno sídlo): {len(ico_in_original_not_in_api)}")
        st.subheader("Sídla pravděpodobně nová - :blue[Nalezena v Aresu ale ne v našem souboru]")
        st.dataframe(ico_in_api_not_in_csv.head(n=30))
        st.subheader("Sídla pravděpodobně zrušená - :red[Nejsou] v Aresu ale v našem souboru jsou")
        st.dataframe(ico_in_original_not_in_api.head(n=30))
        

        # Option to download results
        csv_to_download = ico_in_api_not_in_csv.to_csv(index=False)
        csv_to_download = re.sub(r'IČO', 'ICO', csv_to_download)
        st.download_button(
            label="Stáhnout výsledky jako CSV",
            data=csv_to_download,
            file_name="ico_sidla_ke_kontrole.csv",
            mime="text/csv"
        )

        csv_ares_modified = df_ares_modified.to_csv(index=False)
        csv_ares_modified = re.sub(r'IČO', 'ICO', csv_ares_modified)
        st.download_button(
            label="Stáhnout Ares data do CSV",
            data=csv_ares_modified,
            file_name="ares_api_data.csv",
            mime="text/csv"
        )
        csv_zrusena_sidla = ico_in_original_not_in_api.to_csv(index=False)
        csv_zrusena_sidla_modified = re.sub(r'IČO', 'ICO', csv_zrusena_sidla)
        st.download_button(
            label="Stáhnout zrušená sídla",
            data=csv_zrusena_sidla_modified,
            file_name="zrusena_sidla_passerinvest.csv",
            mime="text/csv"
        )
       

    st.text("Vytvořeno KZ 2024")

if __name__ == "__main__":
    main()

