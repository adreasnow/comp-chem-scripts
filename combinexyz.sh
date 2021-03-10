#!/bin/bash -l
for var in $@
do
	if [ ${var: -4} == ".xyz" ]
		then
		FILE=`basename -s .xyz $var`
		FULLFILEPATH=`readlink -f $var`
		DIRNAME=`dirname $FULLFILEPATH`
		FILEOUT="$DIRNAME/`echo $FILE | cut -d'-' -f1`-`echo $FILE | cut -d'-' -f2`.xyz"
		cat $var >> $FILEOUT
	fi
done