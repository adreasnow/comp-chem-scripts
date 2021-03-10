#!/bin/bash
module load gaussian/g16a03
for var in $@
do
	if [ ${var: -4} == ".chk" ]
	then
		FILE=$var
		FILENAME=`basename -s .chk $FILE`
		FULLFILEPATH=`readlink -f $var`
		FILEPATH=`dirname $FULLFILEPATH`

		formchk $var "$FILEPATH/$FILENAME.fchk"
	fi
done
module unload gaussian/g16a03