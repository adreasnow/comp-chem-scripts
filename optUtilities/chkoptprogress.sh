#!/bin/bash
	filename=`basename -s .out "$@"`
	echo "======================= $filename ======================="
	orcachk=`cat "$@" | grep '* O   R   C   A *'`
	gaussianchk=`cat "$@" | grep 'This is part of the Gaussian(R)'`
	psi4chk=`cat "$@" | grep 'Psi4'`
	if [[ $orcachk != '' ]]; then
		cat "$@" | grep "Item                value                   Tolerance       Converged" -A 5 | tail -6
	elif [[ $gaussianchk != '' ]]; then
		cat "$@" | grep 'Converged' -A 4 | tail -11
	elif [[ $psi4chk != '' ]]; then
		cat "$@" | grep '~'
	fi



