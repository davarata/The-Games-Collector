# The-Games-Collector

My game launcher.

I wanted a single launcher to launch all my games, no matter which emulator was used.

Everything should be driven using a single game descriptor file, which tells the launcher which screens should be turned on or off, which resolution(s) they should be on, how should input be mapped, etc.

This is that launcher.

It consists of plugins for the individual launchers, input mappers and screen handlers (switching screens on/off and changing the resolution).

There are launchers for
- DOSBox
- ScummVM
- Wine
- VirtualBox
- Amiga
- Sega / Nintendo (via RetroArch)
- Native Linux

There are input mappers for
- Remapping keyboard keys (including DOSBox)
- RetroArch (currently only for XBox 360)
- Mapping keyboard keys to a controller (currently only for XBox 360)

# Note
I use the game collector regularly at home, but it is not ready for general public use, amongst others due to lack of documentation and some bugs. It is uploaded here for reference only and is no longer being maintained. I want to replace it with a Scala version.

Feel free to do with this code what you want.

If you want more information about this, feel free to contact me.
