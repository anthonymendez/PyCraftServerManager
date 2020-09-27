import requests
import json
import os

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

    def get_version_list(self, jar_type):
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

    def get_latest_version(self, jar_type):
        return self.get_version_list(jar_type)[0]

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

    def download_by_jar_version_build(self, jar_type, version, build):
        if jar_type == "paper":
            url = self.paper_url
        elif jar_type == "waterfall":
            url = self.waterfall_url
        elif jar_type == "travertine":
            url = self.travertine_url
        else:
            return 1

        # TODO: Error checking

        url += "/" + version + "/" + build + "/download"
        jar_file = requests.get(url)
        jar_file_name = "%s_%s_%s.jar" % (jar_type, version, build)
        open(os.path.join(self.server_jars, jar_file_name), "wb").write(jar_file.content)

    def download_by_jar_version_latest(self, jar_type, version):
        build = self.get_build_latest(jar_type, version)
        return self.download_by_jar_version_build(jar_type, version, build)

    def download_by_jar_latest(self, jar_type):
        version = self.get_latest_version(jar_type)
        return self.download_by_jar_version_latest(jar_type, version)

print(PaperMCServerDownloader("","","").get_version_list("paper"))
print("")
print(PaperMCServerDownloader("","","").get_latest_version("paper"))
print("")
print(PaperMCServerDownloader("","","").get_builds("paper", "1.16.3"))
print("")
print(PaperMCServerDownloader("","","").get_build_latest("paper", "1.16.3"))

PaperMCServerDownloader("","","").download_by_jar_version_build("paper", "1.16.3", "191")
PaperMCServerDownloader("","","").download_by_jar_version_latest("paper", "1.16.3")
PaperMCServerDownloader("","","").download_by_jar_latest("waterfall")
PaperMCServerDownloader("","","").download_by_jar_latest("travertine")