import requests
import json

import logging as log
logging = log.getLogger(__name__)

class PaperMCServerDownloader():

    def __init__(self, main_directory, server_directory, server_jars_folder):
        """
        Initializes Vanilla Server Downloader.\n
        For server_jars_folder, pass in relative location of intended server jars folder. Will create folder if it doesn't exist.
        """
        logging.info("Entry")
        self.versions = []
        self.download_links = {}
        self.main_directory = main_directory
        self.server_directory = server_directory
        self.server_jars = server_jars_folder
        self.paper_url = "https://papermc.io/api/v1/paper"
        self.waterfall_url = "https://papermc.io/api/v1/waterfall"
        self.travertine_url = "https://papermc.io/api/v1/travertine"
        self.head = {
            'Content-type': 'application/json', 
            'Accept': 'application/json'
        }
        logging.info("Exit")

    def get_versions(self, jar_type):
        if jar_type == "paper":
            r = requests.post(url=self.paper_url, headers=self.head)
        elif jar_type == "waterfall":
            r = requests.post(url=self.waterfall_url, headers=self.head)
        elif jar_type == "travertine":
            r = requests.post(url=self.travertine_url, headers=self.head)
        else:
            return 1

        paper_versions = json.loads(r.content)["versions"]
        return paper_versions

    def get_builds(self, jar_type, version):
        if version == None or version == "":
            return 1
        if jar_type == None or jar_type == "":
            return 1

        if jar_type == "paper":
            r = requests.post(url=self.paper_url + "/" + version, headers=self.head)
        elif jar_type == "waterfall":
            r = requests.post(url=self.waterfall_url + "/" + version, headers=self.head)
        elif jar_type == "travertine":
            r = requests.post(url=self.travertine_url + "/" + version, headers=self.head)
        else:
            return 1

        paper_versions = json.loads(r.content)["builds"]
        return paper_versions

    def get_build_latest(self, jar_type, version):
        return self.get_builds(jar_type, version)["latest"]

print(PaperMCServerDownloader("","","").get_versions("paper"))
print(PaperMCServerDownloader("","","").get_builds("paper", "1.16.3"))
print(PaperMCServerDownloader("","","").get_build_latest("paper", "1.16.3"))