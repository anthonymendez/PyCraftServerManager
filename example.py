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
print("\b\tTesting Removing and Adding Options. Should be successful")
print("\bJava Options: " + str(LaunchOptionsHandler.java_options))
print("Game Options: " + str(LaunchOptionsHandler.game_options))
# Remove Java Option
print("Removed Xmx2G: " + str(LaunchOptionsHandler.delete_option("Xmx2G")))
print("Java Options After Remove: " + str(LaunchOptionsHandler.java_options))
# Add Java Option
print("Added Xmx2G: " + str(LaunchOptionsHandler.add_option("Xmx2G", True)))
print("Java Options After Adding: " + str(LaunchOptionsHandler.java_options))
# Remove Game Option
print("Removed nogui: " + str(LaunchOptionsHandler.delete_option("nogui")))
print("Game Options After Remove: " + str(LaunchOptionsHandler.game_options))
# Add Game Option
print("Added nogui: " + str(LaunchOptionsHandler.add_option("nogui", False)))
print("Game Options After Adding: " + str(LaunchOptionsHandler.game_options))
print("\tTesting Removing Options. Should return false")
# Remove Java Options
print("Remove asdf: " + str(LaunchOptionsHandler.delete_option("asdf")))
print(">", end="")