#!/bin/bash

# ./install.sh /opt

mkdir ${1}/the-games-collector
cp ../bin ${1}/the-games-collector -R
cp ../config ${1}/the-games-collector -R
cp ../plugins ${1}/the-games-collector -R
cp ../*.mapper ${1}/the-games-collector
cp ../*.py ${1}/the-games-collector
cp ../*.map ${1}/the-games-collector

ln -s ${1}/the-games-collector/bin/game-launcher.sh /usr/local/bin/game-launcher

TMP_FILE=/tmp/tgc_inst_$(date +%N).sh

find ${1}/the-games-collector -iname *__pycache__* -exec echo "rm '{}' -rf" >> ${TMP_FILE} ';'

sh ${TMP_FILE}
rm ${TMP_FILE}
