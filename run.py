from ServerRunner.VanillaServerRunner import VanillaServerRunner
from WhitelistHandler.WhitelistHandler import WhitelistHandler
from ServerPropertiesHandler.ServerPropertiesHandler import ServerPropertiesHandler


# Server Runner
ServerRunner = VanillaServerRunner("../Vanilla_Server_Basic/")
# Server Properties Handler
ServerPropertiesHandler = ServerPropertiesHandler(ServerRunner)
# Whitelist Handler
WhitelistHandler = WhitelistHandler(ServerRunner)

ServerPropertiesHandler.set_property("server-ip", "0.0.0.0")
ServerPropertiesHandler.set_property("server-port", "25565")

ServerRunner.run()