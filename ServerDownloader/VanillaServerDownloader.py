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
versions = []
download_links = {}

# Function to get Mojang server jar download link

def get_page_download_links(page):
    response = requests.get(page)

    soup = BeautifulSoup(response.text, "html.parser")

    a_container = soup.find_all("a", attrs={"class": "button"})

    # Do not add if client is in link

    if not "client" in a_container[0]["href"]:
        versions.append(page[32::])
        download_links.update({page[32::]: a_container[0]["href"]})

# Start a thread for each page to get the Mojang server jar download link 

for i, page in enumerate(download_pages):
    print("Page %d/%d" % (i, len(download_pages)))
    dp = Thread(target=get_page_download_links, args=[page])
    dp.start()
    thread_q.append(dp)

# Wait for each thread to finish

for t in thread_q:
    t.join()

thread_q.clear()

# Filter out links with client jars (these versions dont have a server jar)

print("Pages downloaded: " + str(len(download_links)))
for link in download_links:
    print(link)

# Make folder to download all server jars

if not os.path.exists("server_jars"):
    os.mkdir("server_jars")

def get_server_jar(version, link):
    file = requests.get(link)
    open(os.path.join("server_jars", str(version) + ".jar"), "wb").write(file.content)

for version in versions:
    link = download_links[version]
    dl_jar = Thread(target=get_server_jar, args=[version, link])
    dl_jar.start()
    thread_q.append(dl_jar)


print("Waiting for downloads to finish")

for t in thread_q:
    t.join()

print("Download done")