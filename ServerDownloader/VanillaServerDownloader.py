import requests
import urllib.request
import time
import os
from bs4 import BeautifulSoup
from threading import Thread

import logging as log
logging = log.getLogger(__name__)

class VanillaServerDownloader():

    def __init__(self, main_directory, server_directory, server_jars_folder):
        """
        Initializes Vanilla Server Downloader.\n
        For server_jars_folder, pass in relative location of intended server jars folder. Will create folder if it doesn't exist.
        """
        logging.info("Entry")
        self.site = "https://mcversions.net"
        self.versions = []
        self.download_links = {}
        self.main_directory = main_directory
        self.server_directory = server_directory
        self.server_jars = server_jars_folder
        logging.info("Exit")

    def parse_mojang_download_links(self):
        """
        Goes through site above and parses each download page for the Mojang download links for server jars.
        """
        logging.info("Entry")
        try:
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
            logging.info("Exit")
            return True
        except Exception as e:
            logging.error("Mojang Download Link scraping failed:\n\t%s", str(e))
            logging.info("Exit")
            return False

    def download_server_jar(self, version):
        """
        Download a server jar based on the given version string.
        """
        logging.info("Entry")
        try:
            if not os.path.exists(self.server_jars):
                os.mkdir(self.server_jars)
            if len(self.download_links) == 0:
                if not self.parse_mojang_download_links():
                    return False
            link = self.download_links.get(version)
            file = requests.get(link)
            open(os.path.join(self.server_jars, str(version) + ".jar"), "wb").write(file.content)
            logging.info("Exit")
            return True
        except Exception as e:
            logging.error("Download of jar %s failed:\n\t%s", str(version), str(e))
            logging.info("Exit")
            return False