#!/bin/bash

mkdir ${1}/icons/16x16/apps -p
mkdir ${1}/icons/22x22/apps -p
mkdir ${1}/icons/24x24/apps -p
mkdir ${1}/icons/32x32/apps -p
mkdir ${1}/icons/48x48/apps -p
mkdir ${1}/icons/64x64/apps -p
mkdir ${1}/icons/128x128/apps -p
mkdir ${1}/icons/256x256/apps -p

python3 ../icon_creator.py --svg=${2} --sizes=16,22,24,32,48,64,128,256 --icon-set-root=${1}/icons --icon-path-pattern=__size__x__size__/apps
