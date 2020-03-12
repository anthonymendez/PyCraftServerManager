from ServerRunner.VanillaServerRunner import VanillaServerRunner
from Configuration.WhitelistHandler import WhitelistHandler
from Configuration.ServerPropertiesHandler import ServerPropertiesHandler
from MiscFunctions.MojangAPI import player_to_uuid

from threading import Thread

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

ServerRunnerThread = Thread(target=VanillaServerRunnerTest.run())

# VanillaServerRunnerTest.run()
server_process = VanillaServerRunnerTest.server_process