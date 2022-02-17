#!/bin/bash -l
module load boost/1.62.0-gcc4
module load zlib/1.2.11

for var in $@
do
	if [ ${var: -5} == ".fchk" ]
	then
		FILE=$var
		FILENAME=`basename -s .fchk $FILE`
		/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel $var -oxyz -O$FILENAME.xyz
	fi
done

module unload boost/1.62.0-gcc4
module unload zlib/1.2.11