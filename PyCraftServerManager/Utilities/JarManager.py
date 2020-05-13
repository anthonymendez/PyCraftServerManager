import os

from shutil import copy

import logging as log
logging = log.getLogger(__name__)

def jar_set(server_directory, server_jars_directory, jar):
    """
    Sets specified jar to use in server folder.

    Checks if jar exists in server_jars folder.

    If so, copies to server folder and sets jar.

    Otherwise, returns False.

    Removes any other jar files in th server folder.

    Run in terminal like so:

    `jar set 1.15.2`

    Returns boolean if it was successful.
    """
    logging.info("Entry")
    # Check if file exists
    jar_path = os.path.join(server_jars_directory, jar + ".jar")
    if not os.path.isfile(jar_path):
        logging.info("Exit")
        return False

    # Remove all .jar files in server directory
    server_dir_files = os.listdir(server_directory)
    for s_d_file in server_dir_files:
        if s_d_file.endswith(".jar"):
            os.remove(os.path.join(server_directory, s_d_file))
            logging.debug("Removed %s.", s_d_file)
    logging.info("Removed all .jars from server folder.")

    # Copy file to server directory
    to_copy_path = os.path.join(server_directory, jar + ".jar")
    try:
        copy(jar_path, to_copy_path)
        logging.info("Copied version to path.")
    except Exception as e:
        logging.error("Could not copy file to server directory. %s", str(e))
        logging.info("Exit")
        return False
    
    logging.info("Exit")
    return True        

def jar_download(ServerDownloader, version):
    """
    Downloads specified server jar in server backups folder.

    Run in terminal like so:

    `jar download 1.15.2`

    Returns boolean if it was successful.
    """
    logging.info("Entry")
    success = ServerDownloader.download_server_jar(version)
    logging.info("Exit")
    return success

def jar_update(ServerDownloader):
    """
    Updates the local download link database of server jars.

    Run in terminal like so:

    `jar update`

    Returns boolean if it was successful.
    """
    logging.info("Entry")
    success = ServerDownloader.parse_download_links()
    logging.info("Exit")
    return success
