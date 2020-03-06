from ServerManager import VanillaServerRunner, ServerPropertiesHandler

VanillaServerRunnerTest = VanillaServerRunner("../Vanilla_Server_Basic/")
ServerPropertiesHandlerTest = ServerPropertiesHandler(VanillaServerRunnerTest)
ServerPropertiesHandlerTest.set_property("server-ip", "127.0.0.1")
ServerPropertiesHandlerTest.set_property("server-port", "5050")
VanillaServerRunnerTest.run()