import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import Document

BASE_URL = "https://www.boe.es"


def fetch_documents():
    """
    Fetch today's BOE documents and save them into the database.
    - Scrapes data from the BOE summary page for today's date.
    - Creates new Document records if they do not already exist.
    Returns:
        int: Number of new documents inserted.
    """
    # Use today's date for BOE URL
    today_str = datetime.now().strftime('%Y/%m/%d')
    url = f"{BASE_URL}/boe/dias/{today_str}/"

    response = requests.get(url)
    if response.status_code != 200:
        return 0  # If page can't be fetched, nothing to add

    soup = BeautifulSoup(response.text, "html.parser")
    count = 0

    doc_date = datetime.now().date()

    for item in soup.select("li.dispo"):
        title_tag = item.select_one("p")
        title = title_tag.text.strip() if title_tag else "Sin título"

        pdf_tag = item.select_one(".puntoPDF a")
        url_doc = BASE_URL + pdf_tag['href'] if pdf_tag else None

        number = None
        if url_doc and "BOE-A" in url_doc:
            number = url_doc.split("/")[-1].replace(".pdf", "")

        # Save to database only if it doesn't exist
        _, created = Document.objects.get_or_create(
            number=number or "N/A",
            date=doc_date,
            defaults={
                "title": title,
                "status": "Publicado",
                "url": url_doc or "N/A",
            }
        )
        if created:
            count += 1

    return count
