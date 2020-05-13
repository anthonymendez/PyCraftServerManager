# PyCraftServerManager

A Python wrapper for Minecraft Servers. Control your Minecraft Server through this Python Package with the normal features + more

# Features

Note: When I say `terminal` or `command line`, I mean feature is accessible through the terminal/command line. When I say `Python`, you can launch the feature in a Python script.

* Start, Stop, Restart Server

* Launch Minecraft and PyCraft commands in the same terminal

* Download Vanilla Minecraft Server Jars

* Configure launch options, whitelist, and server properties through Python and terminal

* Configure server launch Java or Game options. See [`launch_example.properties`](launch_example.properties).

* Backup Server Files as ZIP or TAR through Python and terminal

* Schedule commands using cron-like scheduling. See [APScheduler CronTriggers](https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html) and [How to Schedule like Cron](HOW_TO_CRON.md).

* Delete User Cache through Python and terminal

# Intended Feature List

* Download Spigot, Paper, Forge, SpongeVanilla, and Fabric Minecraft Server Jars

* Launch application through a single executable

# Required

* Python 3 (recommended 3.8) with Pip

* Installation of a Minecraft Server

# Quick Start Installation

1. Clone this repository

1. Run `pip install -r requirements.txt`

1. Modify `run.py` or create your own server starting script.

1. Perform `py run.py` or the equivalent for `run.py` or your script.

1. Run `start` and your server should start up.

# Commands

|    Command Name   |                                                                                                                 Description                                                                                                                | Arguments (blank if none) |
|:-----------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------:|
| start             |  Starts the Minecraft Server.                                                                                                                                                                                                              |                           |
| stop              |  Stop the Minecraft Server.                                                                                                                                                                                                                |                           |
| restart           | Stops then starts the Minecraft server. If Minecraft server isn't running it will not attempt to start it.                                                                                                                                 |                           |
| backup            | Backs up Minecraft server folder to the folder backups in Project directory. Pass in argument "zip" for server folder to be stored in compressed ZIP folder. Pass in argument "tar" for server folder to be stored in compressed TAR file. | ["tar", "zip"]            |
| exit              |  Quits the Python program. Stops Minecraft server if it is still running.                                                                                                                                                                  |                           |
| delete_user_cache | Deletes `usercache.json` in Minecraft server folder.                                                                                                                                                                                       |                           |
| schedule add      | Schedules a command regularly. Uses APScheduler's cron-like structure to do so. See [APScheduler CronTriggers](https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html) and [How to Schedule like Cron](HOW_TO_CRON.md).   | ["Python Command or Server Command to Run"], ["Cron-like string"] |\
| schedule delete   | Deletes a command that is scheduled. Use ID to delete scheduled command from `schedule list` to find out a command's id.                                                                                                                   | [Command ID]              |
| schedule list     | Lists all the currently scheduled commands.                                                                                                                                                                                                |                           |
| jar update | Updates the local download link database of server jars. | |
| jar download  | Downloads the specified jar version into the server_jars folder. | ["Minecraft Version"] |
| jar set | Copies server jar from server_jars folder in to the server folder. Deletes any jar in the server folder. Sets the copied jar file to run from the server folder. | ["Minecraft Version"] |
| launch_options list | Print out the options currently in the launch.properties file. | |
| launch_options add | Add option the launch.properties file. | ["Option"],["True/False"] |
| launch_options delete | Remove option from the launch.properties file. | ["Option"] |
| server_properties list | Print out the properties currently in the server.properties file. | |
| server_properties set | Set a property value in the server.properties file. | ["Property"],["Value"] |
| server_properties get | Gets the value of a property in server.properties file. | ["Property"] |
| whitelist get players | Prints out the list of players from the whitelist. | |
| whitelist get ids | Prints out the list of players and their UUID from the whitelist. | |
| whitelist add | Adds a player to the whitelist. | ["Player Name"] |
| whitelist remove | Removes a player from the whitelist. | ["Player Name"] |

# How-to-Use

In order to use the PyCraftServerManager you can refer to [`run.py`](run.py) or [`example.py`](example.py) on how to use.
