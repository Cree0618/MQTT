import requests

def find_companies_by_address(address):
    base_url = 'https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty-szr/06881777'  # Příklad URL, upravte dle skutečného API
    api_endpoint = '/ekonomicke-subjekty/vyhledat'
    params = {'address': address}
    response = requests.post(f'{base_url}{api_endpoint}', json=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'No data found or API error'}

def extract_company_names_and_ico(data):
    companies = []
    if 'ekonomickeSubjekty' in data:
        for subject in data['ekonomickeSubjekty']:
            name = subject.get('obchodniJmeno', 'Neznámé jméno')
            ico = subject.get('ico', 'Neznámé IČO')
            companies.append({'name': name, 'ico': ico})
    return companies

# Hlavní funkce
address = 'Za Brumlovkou 266/2, 140 00 Praha 4'
response_data = find_companies_by_address(address)
companies = extract_company_names_and_ico(response_data)

for company in companies:
    print(f"Název: {company['name']}, IČO: {company['ico']}")