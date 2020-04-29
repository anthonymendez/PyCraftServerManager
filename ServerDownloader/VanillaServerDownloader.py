import requests
import urllib.request
import time
import os
from bs4 import BeautifulSoup
from threading import Thread

class VanillaServerDownloader():

    def __init__(self):
        """
        Initializes Vanilla Server Downloader.
        """
        self.site = "https://mcversions.net"
        self.versions = []
        self.download_links = {}

    def parse_mojang_download_links(self):
        """
        Goes through site above and parses each download page for the Mojang download links for server jars.
        """
        # Clear versions list and download links dictionary
        self.versions.clear()
        self.download_links.clear()
        # Get each page for a Minecraft version
        response = requests.get(self.site)
        soup = BeautifulSoup(response.text, "html.parser")
        div_container = soup.find_all(attrs={"class": "versions"})
        soup = BeautifulSoup(str(div_container), "html.parser")
        a_container = soup.find_all("a", attrs={"class": "button"})
        download_pages = []
        for a in a_container:
            download_pages.append(self.site + a["href"])

        # Get download link from each page
        thread_q = []

        def get_page_download_links(page):
            response = requests.get(page)
            soup = BeautifulSoup(response.text, "html.parser")
            a_container = soup.find_all("a", attrs={"class": "button"})
            # Do not add if client is in link
            if not "client" in a_container[0]["href"]:
                self.versions.append(page[32::])
                self.download_links.update({page[32::]: a_container[0]["href"]})

        # Start a thread for each page to get the Mojang server jar download link 
        for i, page in enumerate(download_pages):
            dp = Thread(target=get_page_download_links, args=[page])
            dp.start()
            thread_q.append(dp)

        # Wait for each thread to finish
        for t in thread_q:
            t.join()
        thread_q.clear()

    def download_server_jar(self, version):
        """
        Download a server jar based on the given version string.
        """
        if not os.path.exists("server_jars"):
            os.mkdir("server_jars")
        if len(self.download_links) == 0:
            self.parse_mojang_download_links()
        link = self.download_links.get(version)
        file = requests.get(link)
        open(os.path.join("server_jars", str(version) + ".jar"), "wb").write(file.content)