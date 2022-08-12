#!/bin/bash
for var in $@
	do
	filename=`basename -s .out "$var"`
	echo "======================= $filename ======================="
	orcachk=`cat "$var" | grep '* O   R   C   A *'`
	gaussianchk=`cat "$var" | grep 'This is part of the Gaussian(R)'`
	qchemchk=`cat "$var" | grep 'Q-Chem, Inc.,'`
	psi4chk=`cat "$var" | grep 'Psi4'`
	if [[ $orcachk != '' ]]; then
		cat "$var" | grep "Item                value                   Tolerance       Converged" -A 5 | tail -6
	elif [[ $gaussianchk != '' ]]; then
		cat "$var" | grep 'Converged' -A 4 | tail -11
	elif [[ $psi4chk != '' ]]; then
		cat "$var" | grep '~'
	elif [[ "$qchemchk" != '' ]]; then
		cat "$var" | grep 'Maximum     Tolerance    Cnvgd?' -A 3 | tail -9
	fi
	echo ""
done


