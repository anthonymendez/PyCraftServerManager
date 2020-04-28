import requests
import urllib.request
import time
import os
from bs4 import BeautifulSoup

site = "https://mcversions.net"

# Get each page for a Minecraft version

response = requests.get(site)

soup = BeautifulSoup(response.text, "html.parser")

div_container = soup.find_all(attrs={"class": "versions"})

soup = BeautifulSoup(str(div_container), "html.parser")

a_container = soup.find_all("a", attrs={"class": "button"})

download_pages = []

for a in a_container:
    download_pages.append(site + a["href"])

print("Getting download links")

# Get download link from each page

download_links = []

for i, page in enumerate(download_pages):
    print("Page %d/%d" % (i, len(download_pages)))
    response = requests.get(page)

    soup = BeautifulSoup(response.text, "html.parser")

    a_container = soup.find_all("a", attrs={"class": "button"})

    download_links.append(a_container[0]["href"])

print("Done")

print(download_pages)