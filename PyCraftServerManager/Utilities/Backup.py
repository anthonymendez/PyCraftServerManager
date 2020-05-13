import os
import tarfile

from zipfile import ZipFile, ZIP_DEFLATED, ZIP_LZMA, ZIP_BZIP2
from termcolor import colored

import logging as log
logging = log.getLogger(__name__)

def backup_as_zip(server_directory, archive_path):
    """
    Backs up Server folder into a ZIP archive using LZMA compression.
    """
    logging.info("Entry")
    server_zip = ZipFile(archive_path + ".zip", "w", ZIP_LZMA)
    logging.info("Zip file created. Backing up server files.")
    print(colored("Zip file created. Backing up server files.", "green"))
    # os.chdir(server_directory)
    for folder_name, subfolders, file_names in os.walk(server_directory):
        for file_name in file_names:
            # Create complete filepath of file in directory
            file_path = os.path.join(folder_name, file_name)
            # Add file to zip
            server_zip.write(file_path)
            logging.debug("Wrote %s.", str(file_name))
    # os.chdir(self.main_directory)
    logging.info("Exit")

def backup_as_tar(server_directory, archive_path):
    """
    Backs up Server folder into a compressed tar file.
    """
    logging.info("Entry")
    logging.info("Creating and compressing tar file.")
    print(colored("Creating and compressing tar file.", "green"))
    with tarfile.open(archive_path + ".tar.gz", "w:gz") as tar:
        tar.add(server_directory, arcname=os.path.basename(server_directory))
    logging.info("Exit")
