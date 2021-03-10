#!/bin/bash -l

HOMEPATH=`pwd -P`
for var in $@
do
    if [ -d "$var" ]; then
		cd $var

		# delete slurm files
		rm -rf ./slurm*.out

		# move checpoint files into chk dir and delete the g16.* folders
		mkdir chk
		mv g16*/*.chk ./chk
		mv g16*/*.fchk ./chk
		mv *.chk ./chk
		mv *.fchk ./chk
		rm -r g16*

		# move gjf files into input folder (if not already in there)
		mkdir gjf
		mv ./*.gjf ./gjf

		# move slrm files into slrm folder
		mkdir slm
		mv ./*.slm ./slm

		# move log files to oit folder
		mkdir out
		mv ./*.out ./out

		cd $HOMEPATH
	fi
done