from ServerRunner.VanillaServerRunner import VanillaServerRunner
from Configuration.WhitelistHandler import WhitelistHandler
from Configuration.ServerPropertiesHandler import ServerPropertiesHandler
from MiscFunctions.MojangAPI import player_to_uuid

player_to_uuid("Tony_De_Tiger")

# Server Runner
VanillaServerRunnerTest = VanillaServerRunner("../Vanilla_Server_Basic/")

# Server Properties Handler
ServerPropertiesHandlerTest = ServerPropertiesHandler(VanillaServerRunnerTest)
ServerPropertiesHandlerTest.set_property("server-ip", "127.0.0.1")
ServerPropertiesHandlerTest.set_property("server-port", "5050")

# player_to_uuid Handler
print(player_to_uuid("Tony_De_Tiger"))

# Whitelist Handler
WhitelistHandlerTest = WhitelistHandler(VanillaServerRunnerTest)
WhitelistHandlerTest.add_player("Base")
print(WhitelistHandlerTest.get_players())
WhitelistHandlerTest.remove_player("Base")
print(WhitelistHandlerTest.get_players())

# VanillaServerRunnerTest.run()