#/bin/bash

for i in $(find *) ; do
   NAME=$(echo ${i} | sed 's:\.game::g')

   PARAMETERS="--descriptor=${NAME}.game"
   if [ -f ../Icons/${NAME}/${NAME}.svg ] ; then
      PARAMETERS="${PARAMETERS} --icon=../Icons/${NAME}/${NAME}.svg"
   fi

   NAME_BAR=".$(echo ${NAME} | sed 's:.:\.:g')."
   PARAMETERS_BAR=".$(echo ${PARAMETERS} | sed 's:.:\.:g')."

   echo
   echo ".${NAME_BAR}."
   echo ": ${NAME} :"
   echo ":${NAME_BAR}:"
   echo ".${PARAMETERS_BAR}."
   echo ": ${PARAMETERS} :"
   echo ":${PARAMETERS_BAR}:"
   echo

   game-launcher add ${PARAMETERS}

   echo
   echo "-----------"

   read -n 1 -s
done

echo

