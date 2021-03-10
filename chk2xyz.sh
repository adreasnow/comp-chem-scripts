#!/bin/bash -l 
module load gaussian/g16a03
module load boost/1.62.0-gcc4
module load zlib/1.2.11

for var in $@
do
	if [ ${var: -4} == ".chk" ]
	then
		FILE=$var
		FILENAME=`basename -s .chk $FILE`
		formchk $FILE $FILENAME.fchk
		/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel $FILENAME.fchk -oxyz -O$FILENAME.xyz --separate
		rm $FILENAME.fchk
	fi
done

module unload gaussian/g16a03
module unload boost/1.62.0-gcc4
module unload zlib/1.2.11
