import requests
import json
import os

import logging as log
logging = log.getLogger(__name__)

class PaperMCServerDownloader():

    def __init__(self, main_directory, server_directory, server_jars_folder):
        """
        Initializes Vanilla Server Downloader.
        For server_jars_folder, pass in relative location of intended server jars folder. Will create folder if it doesn't exist.
        """
        logging.info("Entry")
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
        """
        Gets a list of available versions to download for the given jar type.
        Example:
        \tInput: "paper"
        \tOutput: "['1.16.3', '1.16.2', '1.16.1', '1.15.2', '1.15.1', '1.15', '1.14.4', '1.14.3', '1.14.2', '1.14.1', '1.14', '1.13.2', '1.13.1', '1.13-pre7', '1.13', '1.12.2', '1.12.1', '1.12', '1.11.2', '1.10.2', '1.9.4', '1.8.8']"
        """
        logging.info("Entry")
        if jar_type == "paper":
            r = requests.post(url=self.paper_url, headers=self.head)
        elif jar_type == "waterfall":
            r = requests.post(url=self.waterfall_url, headers=self.head)
        elif jar_type == "travertine":
            r = requests.post(url=self.travertine_url, headers=self.head)
        else:
            logging.info("Exit")
            return 1

        logging.info("Getting list of %s versions." % jar_type)
        paper_versions = json.loads(r.content)["versions"]
        logging.info("Exit")
        return paper_versions

    def get_latest_version(self, jar_type):
        """
        Gets the latest version of the jar type.
        Example:
        \tInput: "paper"
        \tOutput: "1.16.3"
        """
        logging.info("Entry")
        latest_version = self.get_version_list(jar_type)[0]
        logging.info("Exit")
        return latest_version

    def get_builds(self, jar_type, version):
        """
        Gets a list of available builds for the given jar type and version.
        Example:
        \tInput: "paper", "1.16.3"
        \tOutput: ['206', '205', '204', '203', '202', '201', '200', '199', '198', '197', '196', '195', '194', '193', '192', '191']
        """
        logging.info("Entry")
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
            logging.info("Exit")
            return 1

        logging.info("Getting list of builds for %s version %s." % (jar_type, version))
        paper_versions = json.loads(r.content)["builds"]["all"]
        logging.info("Exit")
        return paper_versions

    def get_build_latest(self, jar_type, version):
        """
        Gets the latest build available for the given jar type and version.
        Example:
        \tInput: "paper", "1.16.3"
        \tOutput: "206"
        """
        logging.info("Entry")
        latest_build = self.get_builds(jar_type, version)[0]
        logging.info("Exit")
        return latest_build

    def download_by_jar_version_build(self, jar_type, version, build):
        """
        Downloads a server jar by the given jar type, version, and build.
        Example:
        \tInput: "paper", "1.16.3", "206"
        \tOutput: File called "paper_1.16.3_206.jar" in server jars folder.
        """
        logging.info("Entry")
        if jar_type == "paper":
            url = self.paper_url
        elif jar_type == "waterfall":
            url = self.waterfall_url
        elif jar_type == "travertine":
            url = self.travertine_url
        else:
            logging.info("Exit")
            return 1

        logging.info("Downloading %s version %s build %s from %s" % (jar_type, version, build, url))
        url += "/" + version + "/" + build + "/download"
        jar_file = requests.get(url)
        jar_file_name = "%s_%s_%s.jar" % (jar_type, version, build)
        open(os.path.join(self.server_jars, jar_file_name), "wb").write(jar_file.content)
        logging.info("Exit")

    def download_by_jar_version_latest(self, jar_type, version):
        """
        Download a server jar by the given jar type, and version, and uses the latest build.
        Example:
        \tInput: "paper", "1.16.3"
        \tOutput: File called "paper_1.16.3_206.jar" in server jars folder.
        """
        logging.info("Entry")
        build = self.get_build_latest(jar_type, version)
        to_return = self.download_by_jar_version_build(jar_type, version, build)
        logging.info("Exit")
        return to_return

    def download_by_jar_latest(self, jar_type):
        """
        Download a server jar by the given jar type, latest version & build.
        Example:
        \tInput: "paper"
        \tOutput: File called "paper_1.16.3_206.jar" in server jars folder.
        """
        logging.info("Entry")
        version = self.get_latest_version(jar_type)
        to_return = self.download_by_jar_version_latest(jar_type, version)
        logging.info("Exit")
        return to_return

## Example on how to use
# print(PaperMCServerDownloader("","","").get_version_list("paper"))
# print(PaperMCServerDownloader("","","").get_latest_version("paper"))
# print(PaperMCServerDownloader("","","").get_builds("paper", "1.16.3"))
# print(PaperMCServerDownloader("","","").get_build_latest("paper", "1.16.3"))

# PaperMCServerDownloader("","","").download_by_jar_version_build("paper", "1.16.3", "191")
# PaperMCServerDownloader("","","").download_by_jar_version_latest("paper", "1.16.3")
# PaperMCServerDownloader("","","").download_by_jar_latest("waterfall")
# PaperMCServerDownloader("","","").download_by_jar_latest("travertine")