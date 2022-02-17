#!/bin/bash -l 
for var in $@
do
	if [ ${var: -4} == ".out" ]
		then
		FILE=`basename -s .out $var`
		echo "==$var=="
		cat $var | grep "Maximum Force"| tail -n 1
		cat $var | grep "RMS     Force"| tail -n 1
		cat $var | grep "Maximum Displacement"| tail -n 1
		cat $var | grep "RMS     Displacement"| tail -n 1
		cat $var | grep "SCF Done:  "| tail -n 1

	fi
done