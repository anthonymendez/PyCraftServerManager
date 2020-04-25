from ServerRunner.VanillaServerRunner import VanillaServerRunner
from MiscFunctions.MojangAPI import player_to_uuid

from threading import Thread

# player_to_uuid Handler
print("Player to UUID Function: %s\n" % player_to_uuid("Tony_De_Tiger"), end="")

# Server Runner
VanillaServerRunnerTest = VanillaServerRunner("../Vanilla_Server_Basic/")

# Server Properties Handler
ServerPropertiesHandlerTest = VanillaServerRunnerTest.ServerPropertiesHandler
ServerPropertiesHandlerTest.set_property("server-ip", "127.0.0.1")
ServerPropertiesHandlerTest.set_property("server-port", "5050")

# Whitelist Handler
WhitelistHandlerTest = VanillaServerRunnerTest.WhitelistHandler

# Launch Options Handler
LaunchOptionsHandler = VanillaServerRunnerTest.LaunchOptionsHandler
print("\bJava Options: " + str(LaunchOptionsHandler.java_options))
print("\bGame Options: " + str(LaunchOptionsHandler.game_options) + ">")