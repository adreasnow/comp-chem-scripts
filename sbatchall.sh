#!/bin/bash -l
DIR=`pwd`
for var in $@
do
	if [ ${var: -4} == ".slm" ]
	then
		cd `dirname "$var"`
		sbatch `basename "$var"`
		cd "$DIR"
	fi
done