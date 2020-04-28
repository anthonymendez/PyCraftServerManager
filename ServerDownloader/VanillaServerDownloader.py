import requests
import urllib.request
import time
import os
from bs4 import BeautifulSoup
from threading import Thread

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

thread_q = []
download_links = []

def get_page_download_links(page):
    response = requests.get(page)

    soup = BeautifulSoup(response.text, "html.parser")

    a_container = soup.find_all("a", attrs={"class": "button"})

    download_links.append({page[32::]: a_container[0]["href"]})

for i, page in enumerate(download_pages):
    print("Page %d/%d" % (i, len(download_pages)))
    dp = Thread(target=get_page_download_links, args=[page])
    dp.start()
    thread_q.append(dp)

for t in thread_q:
    t.join()

print("Pages downloaded: " + str(len(download_links)))
for link in download_links:
    if "client" in link:
        download_links.remove(link)
    print(link)
print("Pages final: " + str(len(download_links)))