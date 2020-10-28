# Configuration
Once the game is installed, use the **configure.sh** script in the bin directory to configure The Games Collector (**TGC**). This will copy all the configuration files to the configuration directory (asked for in the second question) and will help in updating the configuration files.

The script asks a couple of questions in order to determine from where to where files should be copied and what values to put in them. Some questions have values shown in square brackets. This indicates a default answer if no answer is given to the question (enter is pressed without typing in any value). Relative paths can be used. They will be changed to a full path before being saved in the configuration files.

Here is a brief description of each question:

**Type in the path where The Games Collector is installed**
The location where **TGC** is installed. This would have been done by the installation script. A check will be done to see if TGC is installed in _/opt/_ (_/opt/the_games_collector_) or _/usr/local_ (_/usr/local/the_games_collector_) and will be shown in brackets as a default if found in either location.

**Type in the path to the user's home directory [/home/_USER_]**
The directory containing the _.config_ and _.local_ directories. The current user's home directory will be shown in brackets as a default.

**Specify the sizes for which icons should be created (comma-seperated) [16,22,24,32,48,64,96,128,256]**
This indicates which size icons should be created when a game is added. Unless you know what you are doing, just accept the default and press enter.

**Create missing icon directories in '/home/_USER_/.local/share/icons/hicolor/' [y]/n?**
Asks whether any missing directories should be created. Again, just press enter to allow it to create the missing directories. The directory names are based on the sizes as indicated in the previous question: _16x16_, _22x22_, _24x24_, _32x32_, ..., and the first part of the path (_/home/USER_) will match what was entered (or defaulted) in the relevant question above.

**Type in the path where the games are stored**
This path is used as the starting point when locating game files when launching a game. This path, with the path specified in the _Target_ property in the [game descriptor](GameDescriptor.md) file is used as the full path to the game. All games that will be launched by TGC are required to be installed in this location.

**Which launcher is the default DOS launcher**
There are more than one launcher that can launch DOS games (DOSBox, ScummVM and RetroArch). Specify which one should be used by default when launching a DOS game. This tells **TGC** which launcher to use for launching a DOS game if the _Launcher_ property is not specified in the game descriptor file. It is best to use DOSBox. If no value is specified, no configuration will be done for DOS games.

**Which launcher is the default Windows launcher**
There are more than one launcher that can launch Windows games (Wine and ScummVM). Specify which one should be used by default when launching a Windows game. Just as in the previous question, this tells **TGC** which launcher to use. It is best to use Wine. If no value is entered, no configuration will be done for Windows games.

**Type in the path where the DOSBox executable is located**
The path where the **dosbox** executable can be found. A search is done on the path to see if it can be found. If found, it will be shown in brackets as the default. If not found in the path and no value is entered, DOSBox will not be configured.

**Type in the path where the SoundFonts are stored**
This path is used as the starting point when locating a soundfont. This path, with the path specified with the _SoundFont_ property in the [game descriptor](GameDescriptor.md) file is used as the full path to the soundfont. If no value is specified, it will not be configured.

**Type in the path where the FS-UAE executable is located**
The path where the **fs-uae** executable can be found. A search is done on the path to see if it can be found. If found, it will be shown in brackets as the default. If not found in the path and no value is entered, FS-UAE will not be configured.

**Type in the path where the Kickstart ROMs are located**
The path were the Kickstart ROMs are located. It is not important what the files are named, but each ROM file's extension should be _rom_.

**Type in the path where the shaders are located**
The path were the shaders are located. The shaders needs to be XML shader files and the shader file's extension should be _shader_.

**What is the default RetroArch version used?**
**TGC** is able to launch different versions of RetroArch. For each version a configuration file is required. This file needs to be named RetroArch_*VERSION*.cfg. The version of RetroArch that should be used to play the game is specified with the _Launcher_ property in the [game descriptor](GameDescriptor.md) file. If the version is not specified, the version entered here will be used. This value is also used to name the RetroArch configuration file that will be used as the default.

**Type in the path where the RetroArch executable is located**
The path where the **retroarch** executable is located. A search is done on the path to see if it can be found. If found, it will be shown in brackets as the default. If not found in the path and no value is entered, RetroArch will not be configured.

**Type in the path where the RetroArch cores are located**
The path were the cores are located. The script will try to guess where the cores are, relative to the retroarch executable: If the executable is in _RETROARCH/bin/**retroarch**_, it will check if the directory _RETROARCH/**cores**/_ exists. The script currently does not check inside config directory chosen above (_/home/USER/.config/retroarch/_). If the directory _RETROARCH/cores/_ is found, it will be shown in brackets as the default.

**Use my preferred shaders for different cores**
The config file created for the default RetroArch version (RetroArch_*VERSION*.cfg) contains configuration sections that will be used with RetroArch's retroarch.cfg (_/home/USER/.config/retroarch/retroarch.cfg_). Part of that configuration sets the default shaders for the different emulators (commented out by default). By choosing yes, they are uncommented and the partial file name set in the commented out entry is replaced with the full path of that shader. The location of the shaders is required before that can happen and is therefore the next question.

**Type in the path where the RetroArch shaders are located**
The path were the shaders are located. The script will try to guess where the shaders are, relative to the retroarch executable: If the executable is in _RETROARCH/bin/**retroarch**_, it will check if the directory _RETROARCH/**shaders**/_ exists. If the directory _RETROARCH/shaders/_ is found, it will be shown in brackets as the default.

**Type in the path where the ScummVM executable is located**
The path where the **scummvm** executable can be found. A search is done on the path to see if it can be found. If found, it will be shown in brackets as the default.

**Type in the path where the Wine executable is located**
The path where the **wine** executable can be found. A search is done on the path to see if it can be found. If found, it will be shown in brackets as the default.
