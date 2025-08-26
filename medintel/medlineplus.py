import requests
from xml.etree import ElementTree
from bs4 import BeautifulSoup
import streamlit as st

def search_medlineplus(disease: str):
    url = f"https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term={disease}"
    response = requests.get(url)
    root = ElementTree.fromstring(response.content)

    results = []
    for document in root.findall("./list/document"):
        title_el = document.find("content[@name='title']")
        snippet_el = document.find("content[@name='snippet']")

        url_el = (document.find("content[@name='url']") or
                  document.find("content[@name='link']") or
                  document.find("content[@name='FullSummary']"))

        title = title_el.text if title_el is not None else "N/A"
        link = url_el.text if url_el is not None else "N/A"
        snippet = snippet_el.text if snippet_el is not None else "N/A"

        drug_names = []
        if link != "N/A" and "medlineplus.gov" in link:
            try:
                page = requests.get(link, timeout=10)
                soup = BeautifulSoup(page.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    if "/druginfo/" in a["href"]:
                        drug_names.append(a.get_text(strip=True))
            except Exception as e:
                st.warning(f"Failed to fetch {link}: {e}")

        results.append({
            "title": title,
            "snippet": snippet,
            "url": link,
            "drugs": list(set(drug_names))
        })

    return results
