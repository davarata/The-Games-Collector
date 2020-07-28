#!/bin/bash

[ -f all_games ] && rm all_games

RERUN_FAILED_GAMES="N"
SKIP_FAILED_GAMES="N"
SKIP_PASSED_GAMES="N"

if [ -f "failed_games" ] ; then
   VALID_INPUT="N"
   while [ "${VALID_INPUT}" == "N" ] ; do
      echo
      read -p "Rerun failed games [y/n]? "

      if [ "${REPLY}" == "y" ] || [ "${REPLY}" == "Y" ] ; then
         RERUN_FAILED_GAMES="Y"
         VALID_INPUT="Y"
      fi

      if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
         VALID_INPUT="Y"
     fi
   done

   if [ "${RERUN_FAILED_GAMES}" == "N" ] ; then
      VALID_INPUT="N"
      while [ "${VALID_INPUT}" == "N" ] ; do
         echo
         read -p "Skip failed games [y/n]? "

         if [ "${REPLY}" == "y" ] || [ "${REPLY}" == "Y" ] ; then
            SKIP_FAILED_GAMES="Y"
            VALID_INPUT="Y"
         fi

         if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
            VALID_INPUT="Y"
        fi
      done

      if [ "${SKIP_FAILED_GAMES}" == "N" ] ; then
         VALID_INPUT="N"
         while [ "${VALID_INPUT}" == "N" ] ; do
            echo
            read -p "Delete failed games list [y/n]? "

            if [ "${REPLY}" == "y" ] || [ "${REPLY}" == "Y" ] ; then
               VALID_INPUT="Y"
               rm failed_games
            fi

            if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
               VALID_INPUT="Y"
            fi
         done
      fi
   fi
fi

if [ "${RERUN_FAILED_GAMES}" == "N" ] && [ -f "passed_games" ] ; then
   VALID_INPUT="N"
   while [ "${VALID_INPUT}" == "N" ] ; do
      echo
      read -p "Skip passed games [y/n]? "

      if [ "${REPLY}" == "y" ] || [ "${REPLY}" == "Y" ] ; then
         SKIP_PASSED_GAMES="Y"
         VALID_INPUT="Y"
      fi

      if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
         VALID_INPUT="Y"
     fi
   done

   if [ "${SKIP_PASSED_GAMES}" == "N" ] ; then
      VALID_INPUT="N"
      while [ "${VALID_INPUT}" == "N" ] ; do
         echo
         read -p "Delete passed games list [y/n]? "

         if [ "${REPLY}" == "y" ] || [ "${REPLY}" == "Y" ] ; then
            VALID_INPUT="Y"
            rm passed_games
         fi

         if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
            VALID_INPUT="Y"
        fi
      done
   fi
fi

if [ "${RERUN_FAILED_GAMES}" == "Y" ] ; then
   mv failed_games all_games
else
   find ${1} -iname *.game -printf '%f\n' | sed s:.game::g | sort > all_games
   [ -f tmp_all_games ] && rm tmp_all_games
   for i in $(cat all_games) ; do
      if [ "${SKIP_FAILED_GAMES}" == "N" ] ; then
         echo "${i}" >> tmp_all_games
      else
         COUNT=$(cat failed_games | grep -c "${i}")
         if [ "${COUNT}" == "0" ] ; then
            echo "${i}" >> tmp_all_games
         fi
      fi
   done
   rm all_games
   mv tmp_all_games all_games

   for i in $(cat all_games) ; do
      if [ "${SKIP_PASSED_GAMES}" == "N" ] ; then
         echo "${i}" >> tmp_all_games
      else
         COUNT=$(cat passed_games | grep -c "${i}")
         if [ "${COUNT}" == "0" ] ; then
            echo "${i}" >> tmp_all_games
         fi
      fi
   done
   rm all_games
   mv tmp_all_games all_games
fi

for i in $(cat all_games) ; do
   VALID_INPUT="N"
   RUN_GAME="N"
   while [ "${VALID_INPUT}" == "N" ] ; do
      echo
      read -p "Run '${i}' [Y/n/q]? "
      echo

      if [ "${REPLY}" == "y" ] || [ "${REPLY}" == "Y" ] || [ "${REPLY}" == "" ] ; then
         VALID_INPUT="Y"
         RUN_GAME="Y"
         ./test.sh ${i}
      fi

      if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
         VALID_INPUT="Y"
      fi

      if [ "${REPLY}" == "q" ] || [ "${REPLY}" == "Q" ] ; then
         exit
      fi
   done

   VALID_INPUT="N"
   if [ "${RUN_GAME}" == "Y" ] ; then
      while [ "${VALID_INPUT}" == "N" ] ; do
         read -p "Failed [y/n]? "
   
         if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
            VALID_INPUT="Y"
         fi

         if [ "${REPLY}" == "y" ] || [ "${REPLY}" == "Y" ] ; then
            VALID_INPUT="Y"

            if [ -f failed_games ] ; then
               COUNT=$(cat failed_games | grep -c "${i}")
               if [ "${COUNT}" == "0" ] ; then
                  echo "${i}" >> failed_games
               fi
            else
               echo "${i}" > failed_games
            fi
         fi
      done
   fi
   
   if [ "${REPLY}" == "n" ] || [ "${REPLY}" == "N" ] ; then
      echo "${i}" >> passed_games
   fi
   
   echo
   echo "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
   echo "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
done
echo

