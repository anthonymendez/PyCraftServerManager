import os

class ServerRunner:
    def __init__(self, server_folder):
        self.main_dir = os.getcwd()
        self.server_folder = server_folder
        self.server_dir = os.path.join(self.main_dir, server_folder)

    def run(self):
        os.chdir(self.server_dir)
        os.system("java -jar -Xms2G -Xmx2G server.jar nogui")
        os.chdir(self.main_dir)