#!/bin/bash

## Installation location ##

if [ "${1}" == "" ] ; then
   INSTALLATION_LOCATION=
   for i in $(echo "/opt /usr/local") ; do
      if [ -f "${i}/the-games-collector/the-games-collector.py" ] ; then
         INSTALLATION_LOCATION=${i}/the-games-collector
         DEFAULT=" [${INSTALLATION_LOCATION}]"
      fi
   done

   read -p "Type in the path where The Games Collector is installed${DEFAULT}: "
   if [ -z "${REPLY}" ] ; then
      if [ -n "${INSTALLATION_LOCATION}" ] ; then
         echo "Using ${INSTALLATION_LOCATION}"
      else
         echo "Cannot configure The Games Collector without a valid installation."
         exit
      fi
   else
      INSTALLATION_LOCATION=${REPLY}
   fi
else
   echo "Using ${1} as the installation location..."
   echo
   INSTALLATION_LOCATION=${1}
fi

if [ -f "${INSTALLATION_LOCATION}/the-games-collector.py" ] ; then
   INSTALLATION_LOCATION=$(realpath ${INSTALLATION_LOCATION})
else
   echo "${INSTALLATION_LOCATION} does not contain a valid installation for The Games Collector."
   exit
fi


## Home directory ##

if [ "${2}" == "" ] ; then
   read -p "Type in the path to the user's home directory ["${HOME}"]: "
   if [ -z "${REPLY}" ] ; then
      echo "Using '${HOME}'"
      HOME_LOCATION=${HOME}
   else
      HOME_LOCATION=${REPLY}
   fi
else
   echo "Using ${2} as the home location..."
   echo
   HOME_LOCATION=${2}
fi

if [ -d "${HOME_LOCATION}" ] ; then
   HOME_LOCATION=$(realpath ${HOME_LOCATION})
else
   echo "${HOME_LOCATION} does not exist."
   exit
fi


## Config location ##

if [ ! -d "${HOME_LOCATION}/.config" ] ; then
   read -p "'${HOME_LOCATION}/.config' does not exist. Create it [y]/n? "
   [ "${REPLY}" = "Y" ] || [ "${REPLY}" = "y" ] || [ -z "${REPLY}" ] || exit
   mkdir "${HOME_LOCATION}/.config"
fi

CONFIG_LOCATION=${HOME_LOCATION}/.config/the-games-collector

if [ -d ${CONFIG_LOCATION} ] ; then
   read -p "'${CONFIG_LOCATION}' already exists. Use it [y]/n? "
   [ "${REPLY}" = "Y" ] || [ "${REPLY}" = "y" ] || [ -z "${REPLY}" ] || exit
else
   mkdir ${CONFIG_LOCATION}
fi


## Icon creator (icon-creator.cfg) ##

echo
echo " Icons"
echo "-------"

read -p "Specify the sizes for which icons should be created (comma-seperated) [16,22,24,32,48,64,96,128,256]: "
[ -z "${REPLY}" ] && REPLY="16,22,24,32,48,64,96,128,256"
ICON_SIZES=${REPLY}

cp ${INSTALLATION_LOCATION}/config/icon-creator.cfg ${CONFIG_LOCATION}
sed -i 's:Icon set root=:Icon set root='${HOME_LOCATION}'/.local/share/icons/hicolor:' ${CONFIG_LOCATION}/icon-creator.cfg
sed -i 's:Sizes=:Sizes='${ICON_SIZES}':' ${CONFIG_LOCATION}/icon-creator.cfg

read -p "Create missing icon directories in '${HOME_LOCATION}/.local/share/icons/hicolor/' [y]/n? "
if [ "${REPLY}" = "Y" ] || [ "${REPLY}" = "y" ] || [ -z "${REPLY}" ] ; then
   for SIZE in $(echo ${ICON_SIZES} | tr -d " " | sed 's:,: :g') ; do
      if [ -d ${HOME_LOCATION}/.local/share/icons/hicolor/${SIZE}x${SIZE}/apps ] ; then
         echo "${HOME_LOCATION}/.local/share/icons/hicolor/${SIZE}x${SIZE}/apps exists. Skipping..."
      else
         mkdir -p ${HOME_LOCATION}/.local/share/icons/hicolor/${SIZE}x${SIZE}/apps
      fi
   done
fi


## The Games Collector (game-launcher.cfg, GameLauncher.cfg) ##

echo
echo " The Games Collector configuration"
echo "-----------------------------------"

## game-launcher.cfg ##

cp ${INSTALLATION_LOCATION}/config/game-launcher.cfg ${CONFIG_LOCATION}
sed -i 's:Icon set root=:Icon set root='${HOME_LOCATION}'/.local/share/icons/hicolor:' ${CONFIG_LOCATION}/game-launcher.cfg
sed -i 's:Sizes=:Sizes='${ICON_SIZES}':' ${CONFIG_LOCATION}/game-launcher.cfg
sed -i 's:Menu Destination=:Menu Destination='${HOME_LOCATION}'/.local/share/applications:' ${CONFIG_LOCATION}/game-launcher.cfg

read -p "Type in the path where the games are stored: "
while [ -z "${REPLY}" ] ; do
   read -p "Type in the path where the games are stored: "
done

if [ -d "${REPLY}" ] ; then
   sed -i 's:Games Location=:Games Location='${REPLY}':' ${CONFIG_LOCATION}/game-launcher.cfg
else
   echo "The directory '${REPLY}' does not exist."
   exit
fi


## GameLauncher.cfg ##

cp ${INSTALLATION_LOCATION}/config/GameLauncher.cfg ${CONFIG_LOCATION}

CONFIGURE_DOS=NO
read -p "Which launcher is the default DOS launcher: "
if [ -n "${REPLY}" ] ; then
   if [ -f "${INSTALLATION_LOCATION}/config/${REPLY}.cfg" ] ; then
      sed -i 's:DOS=:DOS='${REPLY}':' ${CONFIG_LOCATION}/GameLauncher.cfg
      CONFIGURE_DOS=YES
   else
      echo "The invalid launcher: ${REPLY}"
      exit
   fi
fi

CONFIGURE_WINDOWS=NO
read -p "Which launcher is the default Windows launcher: "
if [ -n "${REPLY}" ] ; then
   if [ -f "${INSTALLATION_LOCATION}/config/${REPLY}.cfg" ] ; then
      sed -i 's:Windows=:Windows='${REPLY}':' ${CONFIG_LOCATION}/GameLauncher.cfg
      CONFIGURE_WINDOWS=YES
   else
      echo "The invalid launcher: ${REPLY}"
      exit
   fi
fi


## DOSBox: (DOSBox.cfg) ##

if [ "${CONFIGURE_DOS}" == "YES" ] ; then
   echo
   echo " DOSBox configuration"
   echo "----------------------"

   EXE_LOCATION=$(which dosbox)
   if [ -n "${EXE_LOCATION}" ] && [ -x "${EXE_LOCATION}" ] ; then
      DEFAULT=" [${EXE_LOCATION}]"
   else
      DEFAULT=""
   fi
   read -p "Type in the path where the DOSBox executable is located${DEFAULT}: "
   if [ -z "${REPLY}" ] ; then
      if [ -n "${EXE_LOCATION}" ] ; then
         echo "Using '${EXE_LOCATION}'"
      else
         echo "Skipping DOSBox configuration."
      fi
   else
      if [ -x ${REPLY} ] ; then
         EXE_LOCATION=${REPLY}
      else
         echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
         exit
      fi
   fi

   if [ -n "${EXE_LOCATION}" ] ; then
      cp ${INSTALLATION_LOCATION}/config/DOSBox.cfg ${CONFIG_LOCATION}
      sed -i 's:Executable=:Executable='${EXE_LOCATION}':' ${CONFIG_LOCATION}/DOSBox.cfg
      sed -i 's:Config location=:Config location='${HOME_LOCATION}'/.dosbox:' ${CONFIG_LOCATION}/DOSBox.cfg

      read -p "Type in the path where the SoundFonts are stored: "
      if [ -n "${REPLY}" ] ; then
         if [ -d "${REPLY}" ] ; then
            sed -i 's:SoundFont Location=:SoundFont Location='${REPLY}':' ${CONFIG_LOCATION}/DOSBox.cfg
         else
            echo "The directory '${REPLY}' does not exist."
            exit
         fi
      else
         echo "Ignoring soundfonts."
      fi
   fi
fi


## FS-UAE: (FS-UAE.cfg) ##

echo
echo " FS UAE configuration"
echo "----------------------"

EXE_LOCATION=$(which fs-uae)
if [ -n "${EXE_LOCATION}" ] && [ -x "${EXE_LOCATION}" ] ; then
   DEFAULT=" [${EXE_LOCATION}]"
else
   DEFAULT=""
fi
read -p "Type in the path where the FS-UAE executable is located${DEFAULT}: "
if [ -z "${REPLY}" ] ; then
   if [ -n "${EXE_LOCATION}" ] ; then
      echo "Using '${EXE_LOCATION}'"
   else
      echo "Skipping FS-UAE configuration."
   fi
else
   if [ -x ${REPLY} ] ; then
      EXE_LOCATION=${REPLY}
   else
      echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
      exit
   fi
fi

if [ -n "${EXE_LOCATION}" ] ; then
   cp ${INSTALLATION_LOCATION}/config/FS-UAE.cfg ${CONFIG_LOCATION}
   sed -i 's:Executable=:Executable='${EXE_LOCATION}':' ${CONFIG_LOCATION}/FS-UAE.cfg

   read -p "Type in the path where the Kickstart ROMs are located: "
   while [ -z "${REPLY}" ] ; do
      read -p "Type in the path where the Kickstart ROMs are located: "
   done

   if [ -d "${REPLY}" ] ; then
      sed -i 's:Kickstart Location=:Kickstart Location='${REPLY}':' ${CONFIG_LOCATION}/FS-UAE.cfg
   else
      echo "The directory '${REPLY}' does not exist."
      exit
   fi

   read -p "Type in the path where the shaders are located: "
   while [ -z "${REPLY}" ] ; do
      read -p "Type in the path where the shaders are located: "
   done

   if [ -d "${REPLY}" ] ; then
      sed -i 's:Shader Location=:Shader Location='${REPLY}':' ${CONFIG_LOCATION}/FS-UAE.cfg
   else
      echo "The directory '${REPLY}' does not exist."
      exit
   fi
fi


## RetroArch: (RetroArch.cfg, RetroArch_VERSION.cfg ##

echo
echo " RetroArch configuration"
echo "-------------------------"

## RetroArch.cfg ##

cp ${INSTALLATION_LOCATION}/config/RetroArch.cfg ${CONFIG_LOCATION}
sed -i 's:Config location=:Config location='${HOME_LOCATION}'/.config/retroarch:' ${CONFIG_LOCATION}/RetroArch.cfg

read -p "What is the default RetroArch version used? "
while [ -z "${REPLY}" ] ; do
   read -p "What is the default RetroArch version used? "
done
VERSION=${REPLY}
sed -i 's:Default Version=:Default Version='${VERSION}':' ${CONFIG_LOCATION}/RetroArch.cfg

# RetroArch_VERSION.cfg ##

EXE_LOCATION=$(which retroarch)
if [ -n "${EXE_LOCATION}" ] && [ -x "${EXE_LOCATION}" ] ; then
   DEFAULT=" [${EXE_LOCATION}]"
else
   DEFAULT=""
fi
read -p "Type in the path where the RetroArch executable is located${DEFAULT}: "
if [ -z "${REPLY}" ] ; then
   if [ -n "${EXE_LOCATION}" ] ; then
      echo "Using '${EXE_LOCATION}'"
   else
      echo "Skipping RetroArch configuration."
   fi
else
   if [ -x ${REPLY} ] ; then
      EXE_LOCATION=${REPLY}
   else
      echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
      exit
   fi
fi

if [ -n "${EXE_LOCATION}" ] ; then
   ## TODO A check should be done since this is an executable.
   cp ${INSTALLATION_LOCATION}/config/RetroArch_VERSION.cfg ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
   sed -i 's:Executable=:Executable='${EXE_LOCATION}':' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg

   CORES_LOCATION=$(dirname ${EXE_LOCATION})
   if [ -d "${CORES_LOCATION}/../cores" ] ; then
      CORES_LOCATION=$(realpath "${CORES_LOCATION}/../cores")
      DEFAULT=" [${CORES_LOCATION}]"
   else
      DEFAULT=""
   fi

   read -p "Type in the path where the RetroArch cores are located${DEFAULT}: "
   if [ -z "${REPLY}" ] ; then
      if [ -n "${CORES_LOCATION}" ] ; then
         echo "Using '${CORES_LOCATION}'"
      else
         while [ -z "${REPLY}" ] ; do
            read -p "Type in the path where the RetroArch cores are located: "
         done
      fi
   else
      if [ -d ${REPLY} ] ; then
         CORES_LOCATION=${REPLY}
      else
         echo "The cores location '${REPLY}' does not exist."
         exit
      fi
   fi
   sed -i 's:Cores Location=:Cores Location='${CORES_LOCATION}':' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg

   read -p "Use my preferred shaders for different cores [Y]/n? "
   if [ "${REPLY}" = "Y" ] || [ "${REPLY}" = "y" ] || [ -z "${REPLY}" ] ; then
      SHADERS_LOCATION=$(dirname ${EXE_LOCATION})
      if [ -d "${SHADERS_LOCATION}/../cores" ] ; then
         SHADERS_LOCATION=$(realpath "${SHADERS_LOCATION}/../shaders")
         DEFAULT=" [${SHADERS_LOCATION}]"
      else
         DEFAULT=""
      fi

      read -p "Type in the path where the RetroArch shaders are located${DEFAULT}: "
      if [ -z "${REPLY}" ] ; then
         if [ -n "${SHADERS_LOCATION}" ] ; then
            echo "Using '${SHADERS_LOCATION}'"
         else
            while [ -z "${REPLY}" ] ; do
               read -p "Type in the path where the RetroArch shaders are located: "
            done
         fi
      else
         if [ -d ${REPLY} ] ; then
            SHADERS_LOCATION=${REPLY}
         else
            echo "The shaders location '${REPLY}' does not exist."
            exit
         fi
      fi

      ## Arcade shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "ntsc-320px-svideo-gauss-scanline.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=Arcade:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=ntsc-320px-svideo-gauss-scanline:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the Arcade core."
         sed -i 's:#video_shader_enable=Arcade:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## DOS shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "crtglow_gauss.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=DOS:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=crtglow_gauss:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the DOS core."
         sed -i 's:#video_shader_enable=DOS:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## Game Boy Advance shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "crtglow_gauss.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=Game Boy Advance:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=crtglow_gauss:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the Game Boy Advance core."
         sed -i 's:#video_shader_enable=Game Boy Advance:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## Master System shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "crtglow_gauss.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=Master System:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=crtglow_gauss:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the Master System core."
         sed -i 's:#video_shader_enable=Master System:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## Mega Drive shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "crtglow_gauss.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=Mega Drive:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=crtglow_gauss:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the Mega Drive core."
         sed -i 's:#video_shader_enable=Mega Drive:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## N64 shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "n64-aa-crt.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=N64:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=n64-aa-crt:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the N64 core."
         sed -i 's:#video_shader_enable=N64:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## NES shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "crtglow_gauss.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=NES:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=crtglow_gauss:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the NES core."
         sed -i 's:#video_shader_enable=NES:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## SNES shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "crtglow_gauss.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=SNES:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=crtglow_gauss:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the SNES core."
         sed -i 's:#video_shader_enable=SNES:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi

      ## ScummVM shader ##
      SHADER_LOCATION=$(find ${SHADERS_LOCATION} -name "crtglow_gauss.*")
      if [ -n "${SHADER_LOCATION}" ] && [ -f "${SHADER_LOCATION}" ] ; then
         sed -i 's:#video_shader_enable=ScummVM:video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
         sed -i 's:#video_shader=crtglow_gauss:video_shader="'${SHADER_LOCATION}'":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      else
         echo "Could not find shader used for the ScummVM core."
         sed -i 's:#video_shader_enable=ScummVM:#video_shader_enable="true":' ${CONFIG_LOCATION}/RetroArch_${VERSION}.cfg
      fi
   fi

fi

## ScummVM: (ScummVM.cfg) ##

echo
echo " ScummVM configuration"
echo "-------------------------"

EXE_LOCATION=$(which scummvm)
if [ -n "${EXE_LOCATION}" ] && [ -x "${EXE_LOCATION}" ] ; then
   DEFAULT=" [${EXE_LOCATION}]"
else
   DEFAULT=""
fi
read -p "Type in the path where the ScummVM executable is located${DEFAULT}: "
if [ -z "${REPLY}" ] ; then
   if [ -n "${EXE_LOCATION}" ] ; then
      echo "Using '${EXE_LOCATION}'"
   else
      echo "Skipping ScummVM configuration."
   fi
else
   if [ -x ${REPLY} ] ; then
      EXE_LOCATION=${REPLY}
   else
      echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
      exit
   fi
fi

if [ -n "${EXE_LOCATION}" ] ; then
   cp ${INSTALLATION_LOCATION}/config/ScummVM.cfg ${CONFIG_LOCATION}
   sed -i 's:Executable=:Executable='${EXE_LOCATION}':' ${CONFIG_LOCATION}/ScummVM.cfg
fi


## Wine: (Wine.cfg) ##

if [ "${CONFIGURE_WINDOWS}" == "YES" ] ; then
   echo
   echo " Wine configuration"
   echo "--------------------"

   EXE_LOCATION=$(which wine)
   if [ -n "${EXE_LOCATION}" ] && [ -x "${EXE_LOCATION}" ] ; then
      DEFAULT=" [${EXE_LOCATION}]"
   else
      DEFAULT=""
   fi
   read -p "Type in the path where the Wine executable is located${DEFAULT}: "
   if [ -z "${REPLY}" ] ; then
      if [ -n "${EXE_LOCATION}" ] ; then
         echo "Using '${EXE_LOCATION}'"
      else
         echo "Skipping Wine configuration."
      fi
   else
      if [ -x ${REPLY} ] ; then
         EXE_LOCATION=${REPLY}
      else
         echo "The executable file '${REPLY}' does not exist or the file is not marked as executable."
         exit
      fi
   fi

   if [ -n "${EXE_LOCATION}" ] ; then
      cp ${INSTALLATION_LOCATION}/config/Wine.cfg ${CONFIG_LOCATION}
      sed -i 's:Executable=:Executable='${EXE_LOCATION}':' ${CONFIG_LOCATION}/Wine.cfg
   fi
fi

echo
echo Done!
echo
