import requests
from bs4 import BeautifulSoup

def get_clean_text(url):
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        texts = []
        for tag in soup.find_all(["h1","h2","h3","p"]):
            t = tag.get_text().strip()
            if len(t) > 40:
                texts.append(t)

        return " ".join(texts).lower()

    except:
        return ""
