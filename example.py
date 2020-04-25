from ServerRunner.VanillaServerRunner import VanillaServerRunner
from MiscFunctions.MojangAPI import player_to_uuid

from threading import Thread

# player_to_uuid Handler
print("Player to UUID Function: %s\n" % player_to_uuid("Tony_De_Tiger"), end="")

# Server Runner
VanillaServerRunnerTest = VanillaServerRunner("../Vanilla_Server_Basic/")

# Server Properties Handler
print("\t")
print("\tTesting Server Properties Handler")
print("\t")
ServerPropertiesHandlerTest = VanillaServerRunnerTest.ServerPropertiesHandler
ServerPropertiesHandlerTest.set_property("server-ip", "127.0.0.1")
ServerPropertiesHandlerTest.set_property("server-port", "5050")

# Whitelist Handler
WhitelistHandlerTest = VanillaServerRunnerTest.WhitelistHandler
print("\t")
print("\tTesting Whitelist Handler")
print("\t")
WhitelistHandlerTest.add_player("Tony_de_Tiger")
WhitelistHandlerTest.add_player("Base4210")
print(WhitelistHandlerTest.get_players())
print(WhitelistHandlerTest.get_players_uuids())
WhitelistHandlerTest.remove_player("Base4210")
print(WhitelistHandlerTest.get_players())
print(WhitelistHandlerTest.get_players_uuids())
WhitelistHandlerTest.add_player("Tony_de_Tiger")

# Launch Options Handler
LaunchOptionsHandlerTest = VanillaServerRunnerTest.LaunchOptionsHandler
print("\t")
print("\tTesting Removing and Adding Options. Should be successful")
print("\t")
print("Java Options: " + str(LaunchOptionsHandlerTest.java_options))
print("Game Options: " + str(LaunchOptionsHandlerTest.game_options))
# Remove Java Option
print("Removed Xmx2G: " + str(LaunchOptionsHandlerTest.delete_option("Xmx2G")))
print("Java Options After Remove: " + str(LaunchOptionsHandlerTest.java_options))
# Add Java Option
print("Added Xmx2G: " + str(LaunchOptionsHandlerTest.add_option("Xmx2G", True)))
print("Java Options After Adding: " + str(LaunchOptionsHandlerTest.java_options))
# Remove Game Option
print("Removed nogui: " + str(LaunchOptionsHandlerTest.delete_option("nogui")))
print("Game Options After Remove: " + str(LaunchOptionsHandlerTest.game_options))
# Add Game Option
print("Added nogui: " + str(LaunchOptionsHandlerTest.add_option("nogui", False)))
print("Game Options After Adding: " + str(LaunchOptionsHandlerTest.game_options))
print("\tTesting Removing Options. Should return false")
# Remove Java Options
print("Remove asdf: " + str(LaunchOptionsHandlerTest.delete_option("asdf")))
print(">", end="")