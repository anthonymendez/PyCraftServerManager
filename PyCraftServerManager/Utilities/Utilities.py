import os

import logging as log
logging = log.getLogger(__name__)

def is_windows():
    """
    Checks if OS is windows. Returns bool.
    """
    logging.info("Entry")
    return os.name == "nt"
    logging.info("Exit")

def enable_eula(server_directory):
    """
    Enables EULA for the given server directory. Returns bool if successful.
    """
    logging.info("Entry")
    # Check if it exists
    eula_path = os.path.join(server_directory, "eula.txt")
    if not os.path.isfile(eula_path):
        # Create eula.txt
        try:
            logging.info("Creating eula with \"eula=true\".")
            open(eula_path, "w").write("eula=true")
            logging.info("Exit")
            return True
        except Exception as e:
            logging.error("Could not create eula. %s", str(e))
            logging.info("Exit")
            return False

    # If it does exist, just write eula=true
    try:
        logging.info("Writing to eula with \"eula=true\".")
        open(eula_path, "w").write("eula=true")
        logging.info("Exit")
        return True
    except Exception as e:
        logging.error("Could not write to eula. %s", str(e))
        logging.info("Exit")
        return False