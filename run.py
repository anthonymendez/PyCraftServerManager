from ServerRunner.VanillaServerRunner import VanillaServerRunner
from Configuration.WhitelistHandler import WhitelistHandler
from Configuration.ServerPropertiesHandler import ServerPropertiesHandler


# Server Runner
ServerRunner = VanillaServerRunner("../Vanilla_Server_Basic/")

# Server Properties Handler
ServerPropertiesHandler = ServerPropertiesHandler(ServerRunner)
# Whitelist Handler
WhitelistHandler = WhitelistHandler(ServerRunner)

# Set IP and Server Port
ServerPropertiesHandler.set_property("server-ip", "0.0.0.0")
ServerPropertiesHandler.set_property("server-port", "25565")

ServerRunner.run()