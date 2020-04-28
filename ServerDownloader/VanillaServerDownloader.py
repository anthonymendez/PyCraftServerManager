import requests
import urllib.request
import time
import os
from bs4 import BeautifulSoup

site = "https://mcversions.net"

response = requests.get(site)

soup = BeautifulSoup(response.text, "html.parser")

div_container = soup.find_all(attrs={"class": "versions"})

soup = BeautifulSoup(str(div_container), "html.parser")

a_container = soup.find_all("a", attrs={"class": "button"})

for a in a_container:
    print(site + a["href"])