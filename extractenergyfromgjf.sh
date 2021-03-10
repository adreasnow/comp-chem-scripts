#!/bin/bash -l
module load boost/1.62.0-gcc4
module load zlib/1.2.11
echo "Filename, Energy (Eh)" > out.csv

mkdir ./xyz
for var in $@
do
	if [ ${var: -4} == ".out" ]
		then
		MAXFORCESTRING=`cat $var | grep "Maximum Force"| tail -n 1`
		RMSFORCESTRING=`cat $var | grep "RMS     Force"| tail -n 1`
		MAXDISPSTRING=`cat $var | grep "Maximum Displacement"| tail -n 1`
		RMSDISPSTRING=`cat $var | grep "RMS     Displacement"| tail -n 1`
		SCFSTRING=`cat $var | grep "SCF Done:  "| tail -n 1`

		MAXFORCE=${MAXFORCESTRING: -3}
		RMSFORCE=${RMSFORCESTRING: -3}
		MAXDISP=${MAXDISPSTRING: -3}
		RMSDISP=${RMSDISPSTRING: -3}

		if [[ $MAXFORCE == YES ]] || [[ $RMSFORCE == YES ]] || [[ $MAXDISP == YES ]] || [[ $RMSDISP == YES ]]; then

			FOLDER=`dirname $var | awk -F/ '{print $NF}'`
			FILE=`basename -s .out $var`
			echo "==$var=="
			ENERGY=`echo $SCFSTRING | cut -d ' ' -f 5`
			echo "$FOLDER-$FILE, $ENERGY" >> out.csv

			/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel $var -oxyz -O./xyz/$FOLDER-$FILE.xyz

			cat ./xyz/$FOLDER-$FILE.xyz >> ./xyz/$FOLDER.xyz
			rm ./xyz/$FOLDER-$FILE.xyz




		fi
	fi
done

module unload boost/1.62.0-gcc4
module unload zlib/1.2.11
