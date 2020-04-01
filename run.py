from ServerRunner.VanillaServerRunner import VanillaServerRunner


# Server Runner
ServerRunner = VanillaServerRunner("../Vanilla_Server_Basic/")

# Server Properties Handler
ServerPropertiesHandler = ServerRunner.ServerPropertiesHandler
# Whitelist Handler
WhitelistHandler = ServerRunner.WhitelistHandler

# Set IP and Server Port
ServerPropertiesHandler.set_property("server-ip", "0.0.0.0")
ServerPropertiesHandler.set_property("server-port", "25565")