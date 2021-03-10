#!/bin/bash -l
echo "base_name,ion_class,ion_name,homo,lumo,gap,nbo_homo,nbo_lumo,nbo_gap"     						> ./homo-lumo.csv

HOMEPATH=`pwd -P`
for var in $@
do
	if [ ${var: -4} == ".out" ]; then
		FULLFILEPATH=`readlink -f $var`
		FILEPATH=`dirname $FULLFILEPATH`
		FILENAME=`/bin/basename -s .out $FULLFILEPATH`
		if [[ $FILENAME != 'slurm'* ]]; then
			echo "===$FILENAME==="
			IONNAME=`echo $FILENAME | cut -d'-' -f2`
			NEUTRALNAME=`echo $FILENAME | cut -d'-' -f1`
			HOMOENG=`cat $FULLFILEPATH | sed '1,/Orbital energies and kinetic energies/d' | grep 'O     ' | grep -v 'NBO' | tail -n 3 | grep O -m 1 | tr -s ' ' | cut -d' ' -f 4`
			LUMOENG=`cat $FULLFILEPATH | sed '1,/Orbital energies and kinetic energies/d' | grep -m 1 'V     ' | tr -s ' ' | cut -d' ' -f4` 
			# HOMOEV=`echo "$HOMOENG * 27.211386" | bc`
			# LUMOEV=`echo "$LUMOENG * 27.211386" | bc`
			# HOMOLUMOEV=`echo "($LUMOEV) - ($HOMOEV)" | bc`
			# NBOHOMOENG=`cat $FULLFILEPATH | grep " 1. BD" | tail -n 1 | tr -s ' ' | cut -d' ' -f 12`
			# NBOLUMOENG=`cat $FULLFILEPATH | grep "Molecular unit  1" -A 100 |grep 'RY' -m1 | tr -s ' ' | cut -d' ' -f8`
			# NBOHOMOEV=`echo "$NBOHOMOENG * 27.211386" | bc`
			# NBOLUMOEV=`echo "$NBOLUMOENG * 27.211386" | bc`
			# NBOHOMOLUMOEV=`echo "($NBOLUMOEV)-($NBOHOMOEV)" | bc`



			if [[ $FILENAME == *'BF2(CF3)2' ]] || [[ $FILENAME == *'BF4' ]] || [[ $FILENAME == *'C(CN)3' ]] || [[ $FILENAME == *'N(SOOCF3)2' ]] || [[ $FILENAME == *'Cl' ]] || [[ $FILENAME == *'N(NC)2' ]] || [[ $FILENAME == *'tempo' ]]; then
				CLASS="anion"
			elif [[ $FILENAME == *'C1MPyr' ]] || [[ $FILENAME == *'ImidMe2' ]] || [[ $FILENAME == *'NMe4' ]] || [[ $FILENAME == *'PMe4' ]] || [[ $FILENAME == *'Na' ]] || [[ $FILENAME == *'Li' ]]; then
				CLASS="cation"
			elif [[ $FILENAME == *'Pd' ]] || [[ $FILENAME == *'Ni' ]]; then
				CLASS="metal"
			fi
			echo "$NEUTRALNAME,$CLASS,$IONNAME,$HOMOENG,$LUMOENG" >> ./homo-lumo.csv
		fi
	fi
done
