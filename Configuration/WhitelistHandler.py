from Utilities.MojangAPI import player_to_uuid
import os
import json

class WhitelistHandler:
    """
    Whitelist Handler handles adding, removing, and showing players from the whitelist.
    """

    whitelist_json = "whitelist.json"

    def __init__(self, main_directory, server_directory):
        """
        Initializes Server Properties Handler by tying it to a Server Director.
        """
        # Store all current server properties
        self.main_directory = main_directory
        self.server_directory = server_directory

    def get_players(self):
        """
        Returns list of player names in whitelist.
        """
        player_names = []
        os.chdir(self.server_directory)
        try:
            with open(WhitelistHandler.whitelist_json) as json_file:
                whitelist = json.load(json_file)
                for player_uuid_json in whitelist:
                    name = player_uuid_json["name"]
                    player_names.append(name)
        except json.decoder.JSONDecodeError:
            print("Couldn't decode JSON")
        os.chdir(self.main_directory)
        return player_names

    def get_players_uuids(self):
        """
        Returns list of player names and their uuid.
        """
        player_uuids = []
        os.chdir(self.server_directory)
        try:
            with open(WhitelistHandler.whitelist_json, "r") as json_file:
                whitelist = json.load(json_file)
                for player_uuid_json in whitelist:
                    name = player_uuid_json["name"]
                    uuid = player_uuid_json["uuid"]
                    player_uuid = {
                        "uuid": uuid,
                        "name": name
                    }
                    player_uuids.append(player_uuid)
        except json.decoder.JSONDecodeError:
            print("Couldn't decode JSON")
        os.chdir(self.main_directory)
        return player_uuids

    def remove_player(self, player_name):
        """
        Removes player from the whitelist.
        """
        os.chdir(self.server_directory)
        # Remove from local object
        with open(WhitelistHandler.whitelist_json, "r") as json_file:
            whitelist = json.load(json_file)
            for i in range(len(whitelist)):
                if whitelist[i]["name"] == player_name:
                    whitelist.pop(i)
                    break
        # Save changes to whitelist file
        open(WhitelistHandler.whitelist_json, "w").write(
            json.dumps(whitelist, sort_keys=True, indent=4, separators=(",", ": "))
        )
        os.chdir(self.main_directory)

    def add_player(self, player_name):
        """
        Adds a player to the whitelist.
        """
        os.chdir(self.server_directory)
        # Remove from local object
        try:
            with open(WhitelistHandler.whitelist_json, "r") as json_file:
                whitelist = json.load(json_file)
                player_name = player_to_uuid(player_name)
                whitelist.append(player_name)
        except json.decoder.JSONDecodeError:
            print("Couldn't decode JSON, possibly empty?")
            player_name = player_to_uuid(player_name)
            whitelist = []
            whitelist.append(player_name)

        # Save changes to whitelist file
        open(WhitelistHandler.whitelist_json, "w").write(
            json.dumps(whitelist, sort_keys=True, indent=4, separators=(",", ": "))
        )
        os.chdir(self.main_directory)
