import requests
import json

import logging as log
logging = log.getLogger(__name__)

def player_to_uuid(player_name):
    """
    Returns uuid and playername in a dict of a given player name.\n
    Example:\n
    \tInput: \"Tony_De_Tiger\"\n
    \tOutput: {"uuid":"662a4856593c412ea148acf5d829ef56","name":"Tony_De_Tiger"}\n
    """
    logging.info("Entry")
    url = "https://api.mojang.com/profiles/minecraft"
    data = json.dumps(player_name)
    head = {
        'Content-type': 'application/json', 
        'Accept': 'application/json'
        }
    logging.debug("Getting: %s", str(player_name))
    r = requests.post(url=url, data=data, headers=head)
    uuid_player_json = json.loads(r.content)
    player_uuid_dict = {
        "name": uuid_player_json[0]["name"],
        "uuid": uuid_player_json[0]["id"]
    }
    logging.debug("Received: %s", str(player_uuid_dict))
    logging.info("Exit")
    return player_uuid_dict