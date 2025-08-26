from bs4 import BeautifulSoup

def html_to_text(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n", strip=True)
