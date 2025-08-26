import requests

def fetch_drug_label(drug: str):
    base_url = "https://api.fda.gov/drug/label.json"
    params = {"search": f"openfda.brand_name:{drug}", "limit": 5}
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception:
        return []
