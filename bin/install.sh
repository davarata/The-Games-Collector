#!/bin/bash

# TODO convert to python script

INSTALL_DIR=$(pwd | sed 's:\ :\\\ :g')

if [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/bin/game-launcher.sh" ] ; then
    if [ -e /usr/local/bin/game-launcher ] ; then
		echo "/usr/local/bin/game-launcher found. Skipping..."
	else
		sudo ln -s ${INSTALL_DIR}/bin/game-launcher.sh /usr/local/bin/game-launcher
	fi
else
	echo "Error: ${INSTALL_DIR}/bin/game-launcher.sh not found"
    exit 1
fi

if [ -d ~/.local/share/icons/hicolor/16x16/apps ] ; then
	echo "~/.local/share/icons/hicolor/16x16/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/16x16/apps
fi

if [ -d ~/.local/share/icons/hicolor/22x22/apps ] ; then
	echo "~/.local/share/icons/hicolor/22x22/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/22x22/apps
fi

if [ -d ~/.local/share/icons/hicolor/24x24/apps ] ; then
	echo "~/.local/share/icons/hicolor/24x24/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/24x24/apps
fi

if [ -d ~/.local/share/icons/hicolor/32x32/apps ] ; then
	echo "~/.local/share/icons/hicolor/32x32/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/32x32/apps
fi

if [ -d ~/.local/share/icons/hicolor/48x48/apps ] ; then
	echo "~/.local/share/icons/hicolor/48x48/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/48x48/apps
fi

if [ -d ~/.local/share/icons/hicolor/64x64/apps ] ; then
	echo "~/.local/share/icons/hicolor/64x64/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/64x64/apps
fi

if [ -d ~/.local/share/icons/hicolor/128x128/apps ] ; then
	echo "~/.local/share/icons/hicolor/128x128/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/128x128/apps
fi

if [ -d ~/.local/share/icons/hicolor/256x256/apps ] ; then
	echo "~/.local/share/icons/hicolor/256x256/apps exists. Skipping..."
else
	mkdir -p ~/.local/share/icons/hicolor/256x256/apps
fi

