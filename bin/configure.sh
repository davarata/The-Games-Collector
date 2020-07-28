#!/bin/bash

INSTALL_ROOT="/opt/the-games-collector"

## The Games Collector (game-launcher.cfg, GameLauncher.cfg) ##
echo
echo " The Games Collector configuration"
echo "-----------------------------------"

HOME_DIR=
read -p "Type in the home directory path where the configuration will be stored ["$(echo ~)"]: "
if [ -z "${REPLY}" ] ; then
    echo "Using '${HOME}'"
    USER_HOME=${HOME}
else
    if [ ! -d ${REPLY} ] ; then
        echo "${REPLY} does not exist."
        exit
    fi

   USER_HOME=${REPLY}
fi

if [ -d ${USER_HOME}/.config/the-games-collector ] ; then
    read -p "'${USER_HOME}/.config/the-games-collector' already exists. Use it [y]/n?"
    [ "${REPLY}" = "Y" ] || [ "${REPLY}" = "y" ] || [ -z "${REPLY}" ] || exit
else
    mkdir ${USER_HOME}/.config/the-games-collector
fi

## game-launcher.cfg ##
cp ${INSTALL_ROOT}/config/game-launcher.cfg ${USER_HOME}/.config/the-games-collector

sed -i 's:Menu Destination=:Menu Destination='${USER_HOME}'/.local/share/applications:' ${USER_HOME}/.config/the-games-collector/game-launcher.cfg

read -p "Type in the path where the games are stored: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the games are stored: "
done

if [ -d "${REPLY}" ] ; then
    sed -i 's:Games Location=:Games Location='${REPLY}':' ${USER_HOME}/.config/the-games-collector/game-launcher.cfg
else
    echo "The directory '${REPLY}' does not exist."
    exit
fi

sed -i 's:Icon set root=:Icon set root='${USER_HOME}'/.local/share/icons/hicolor:' ${USER_HOME}/.config/the-games-collector/game-launcher.cfg

## Icon creator (icon-creator.cfg) ##
cp ${INSTALL_ROOT}/config/icon-creator.cfg ${USER_HOME}/.config/the-games-collector
sed -i 's:Icon set root=:Icon set root='${USER_HOME}'/.local/share/icons/hicolor:' ${USER_HOME}/.config/the-games-collector/icon-creator.cfg

## Icons  ##
echo
echo " Icons"
echo "-------"

read -p "Specify the sizes for which icons should be created (comma-seperated) [16,22,24,32,48,64,96,128,256]: "
[ -z "${REPLY}" ] && REPLY="16,22,24,32,48,64,96,128,256"
ICON_SIZES=${REPLY}
sed -i 's:Sizes=:Sizes='${ICON_SIZES}':' ${USER_HOME}/.config/the-games-collector/game-launcher.cfg
sed -i 's:Sizes=:Sizes='${ICON_SIZES}':' ${USER_HOME}/.config/the-games-collector/icon-creator.cfg

read -p "Create missing icon directories in '${USER_HOME}/.local/share/icons/hicolor/'? [y]/n?"
if [ "${REPLY}" = "Y" ] || [ "${REPLY}" = "y" ] || [ -z "${REPLY}" ] ; then
    for SIZE in $(echo ${ICON_SIZES} | tr -d " " | sed 's:,: :g') ; do
        if [ -d ${USER_HOME}/.local/share/icons/hicolor/${SIZE}x${SIZE}/apps ] ; then
    	    echo "${USER_HOME}/.local/share/icons/hicolor/${SIZE}x${SIZE}/apps exists. Skipping..."
        else
        	mkdir -p ${USER_HOME}/.local/share/icons/hicolor/${SIZE}x${SIZE}/apps
        fi
    done
fi

## GameLauncher.cfg ##
echo
echo " Defaults"
echo "----------"

cp ${INSTALL_ROOT}/config/GameLauncher.cfg ${USER_HOME}/.config/the-games-collector

read -p "Which launcher is the default DOS launcher: "
while [ -z "${REPLY}" ] ; do
    read -p "Which launcher is the default DOS launcher: "
done

if [ -f "${INSTALL_ROOT}/config/${REPLY}.cfg" ] ; then
    sed -i 's:DOS=:DOS='${REPLY}':' ${USER_HOME}/.config/the-games-collector/GameLauncher.cfg
else
    echo "The invalid launcher: ${REPLY}"
    exit
fi

read -p "Which launcher is the default Windows launcher: "
while [ -z "${REPLY}" ] ; do
    read -p "Which launcher is the default Windows launcher: "
done

if [ -f "${INSTALL_ROOT}/config/${REPLY}.cfg" ] ; then
    sed -i 's:Windows=:Windows='${REPLY}':' ${USER_HOME}/.config/the-games-collector/GameLauncher.cfg
else
    echo "The invalid launcher: ${REPLY}"
    exit
fi


## DOSBox: (DOSBox.cfg) ##
echo
echo " DOSBox configuration"
echo "----------------------"

cp ${INSTALL_ROOT}/config/DOSBox.cfg ${USER_HOME}/.config/the-games-collector
sed -i 's:Config location=:Config location='${USER_HOME}'/.dosbox:' ${USER_HOME}/.config/the-games-collector/DOSBox.cfg

read -p "Type in the path where the SoundFonts are stored: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the SoundFonts are stored: "
done

if [ -d "${REPLY}" ] ; then
    sed -i 's:SoundFont Location=:SoundFont Location='${REPLY}':' ${USER_HOME}/.config/the-games-collector/DOSBox.cfg
else
    echo "The directory '${REPLY}' does not exist."
    exit
fi

read -p "Type in the path where the DOSBox executable is located: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the DOSBox executable is located: "
done

if [ -x "${REPLY}" ] ; then
    sed -i 's:Executable=:Executable='${REPLY}':' ${USER_HOME}/.config/the-games-collector/DOSBox.cfg
else
    echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
    exit
fi


## FS-UAE: (FS-UAE.cfg) ##
echo
echo " FS UAE configuration"
echo "----------------------"

cp ${INSTALL_ROOT}/config/FS-UAE.cfg ${USER_HOME}/.config/the-games-collector

read -p "Type in the path where the FS-UAE executable is located: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the FS-UAE executable is located: "
done

if [ -x "${REPLY}" ] ; then
    sed -i 's:Executable=:Executable='${REPLY}':' ${USER_HOME}/.config/the-games-collector/FS-UAE.cfg
else
    echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
    exit
fi

read -p "Type in the path where the Kickstart ROMs are located: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the Kickstart ROMs are located: "
done

if [ -d "${REPLY}" ] ; then
    sed -i 's:Kickstart Location=:Kickstart Location='${REPLY}':' ${USER_HOME}/.config/the-games-collector/FS-UAE.cfg
else
    echo "The directory '${REPLY}' does not exist."
    exit
fi

read -p "Type in the path where the shaders are located: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the shaders are located: "
done

if [ -d "${REPLY}" ] ; then
    sed -i 's:Shader Location=:Shader Location='${REPLY}':' ${USER_HOME}/.config/the-games-collector/FS-UAE.cfg
else
    echo "The directory '${REPLY}' does not exist."
    exit
fi


## RetroArch: (RetroArch.cfg) ##
echo
echo " RetroArch configuration"
echo "-------------------------"

cp ${INSTALL_ROOT}/config/RetroArch.cfg ${USER_HOME}/.config/the-games-collector
sed -i 's:Config location=:Config location='${USER_HOME}'/.config/retroarch:' ${USER_HOME}/.config/the-games-collector/RetroArch.cfg

read -p "What is the default RetroArch version used?: "
sed -i 's:Default Version=:Default Version='${REPLY}':' ${USER_HOME}/.config/the-games-collector/RetroArch.cfg


## ScummVM: (ScummVM.cfg) ##
echo
echo " ScummVM configuration"
echo "-------------------------"

cp ${INSTALL_ROOT}/config/ScummVM.cfg ${USER_HOME}/.config/the-games-collector
read -p "Type in the path where the ScummVM executable is located: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the ScummVM executable is located: "
done

if [ -x "${REPLY}" ] ; then
    sed -i 's:Executable=:Executable='${REPLY}':' ${USER_HOME}/.config/the-games-collector/ScummVM.cfg
else
    echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
    exit
fi


## Wine: (Wine.cfg) ##
echo
echo " Wine configuration"
echo "--------------------"

cp ${INSTALL_ROOT}/config/Wine.cfg ${USER_HOME}/.config/the-games-collector
read -p "Type in the path where the Wine executable is located: "
while [ -z "${REPLY}" ] ; do
    read -p "Type in the path where the Wine executable is located: "
done

if [ -x "${REPLY}" ] ; then
    sed -i 's:Executable=:Executable='${REPLY}':' ${USER_HOME}/.config/the-games-collector/Wine.cfg
else
    echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
    exit
fi

echo
echo Done!
echo

exit

FS-UAE (FS-UAE.cfg)
-------------------
Config location=N/A

[Launcher]
Executable=/usr/bin/fs-uae
Kickstart Location=/village/gebruikers/rebit/tydelik/ksroms
Shader Location=/village/gebruikers/rebit/tydelik/XML Shaders/v1.0
