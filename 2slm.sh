#!/bin/bash
DIR=`pwd`
print_usage() {
	echo """
	Usage: 2slm -d [DAYS] -h [HOURS] -s -m [MEM (GB)] -n [TPN] -c [PROCS] -p [PARTITIONS] -e -q [QOS] -t -C [FILE1] -C [FILE2] [INPUT FILES]...

	Arguments
	  [FILE] the files to be converted into slurm fils

	MANDATORY ###############################################################
		 --if no time flag is set, the script will defalt to 24 hours--
		                    --only use one fo these--

	  -d days allowed for the job to run. 
	    if more granularity is needed, then use -h

	  -h hours allowed for the job to run in the format HH
	    superseeds -d

	  -s uses the shortest settings and queues
	    24 hours for MonARCH (same as not setting any time flag)
	    30 minutes for Massive

	OPTIONAL ################################################################
	  -m memory allowed in GB (not Gb)
	    will be automatically populated if specified in the job file

	  -n tasks per node
	    defaults to the number of procs

	  -c the amount of procs (CPUs) allowd for the job to run
	    will be automatically populated if specified in the job file

	  -C list any files to copy, relative to the current dir

	  -p the partitons to be specified as comma separated values
	    comp,short will be automatically applied where needed

	  -e sends an email to the user, as pulled form the system variable $EMAIL
	    set this in your rc file

	  -q qos specification

	  -t this flag tells the ccript to 'touch' the log file. 
	    this forces the script to make sure that the logfile exists before the slurm job is run

	  -S Submits job via SLURM

	  -D SLURM dependency ('-d afterany:<JOBID>')

	###########################################################################
	  This script creates a file structure from the current directory like this

	  |-name.(in|inp|gjf)
	  |-name.slm
	  |-name/ (for non gaussian jobs)
	    |-<Scratch>
	    |-name.out (moved at job completion)
	  |-g16.#######/ (only for gaussian jobs)
	    |-checkpoint.chk
	"""
}

setupscratch() {
	echo "mkdir \"$SCRATCH/$FILENAME\""													>> "$FILEPATH/$FILENAME.slm"
	echo "cp \"$FULLFILEPATH\" \"$SCRATCH/$FILENAME\""									>> "$FILEPATH/$FILENAME.slm"		
	echo "cd \"$SCRATCH/$FILENAME\""													>> "$FILEPATH/$FILENAME.slm"	
}

copyscratch() {
	echo "mkdir \"$FILEPATH/$FILENAME\""															>> "$FILEPATH/$FILENAME.slm"
	echo "cp $SCRATCH/$FILENAME/* \"$FILEPATH/$FILENAME/\" && rm -rf \"$SCRATCH/$FILENAME\""		>> "$FILEPATH/$FILENAME.slm"
	echo "mv \"$FILEPATH/$FILENAME.out\" \"$FILEPATH/$FILENAME/\""									>> "$FILEPATH/$FILENAME.slm"
}

copyfiles() {
	for var in ${files2copy[@]}; do
		COPYFILEPATH=`readlink -f $var`
		echo "cp \"$COPYFILEPATH\" \"$SCRATCH/$FILENAME\""									>> "$FILEPATH/$FILENAME.slm"
	done
}

	hours="none"
	mem="none"
	tpn="none"
	procs="none"
	part="none"
	days="none"
	email="false"
	qos="none"
	short="false"
	submit="false"
	touchfile="false"
	depjob="false"

while getopts 'h:m:n:c:p:d:t:C:D:sSeq:' flag "${@}"; do
  case "$flag" in
	h) hours=$OPTARG;;
	m) mem="$OPTARG";;
	n) tpn="$OPTARG";;
	c) procs="$OPTARG";;
	p) part="$OPTARG";;
	d) days="$OPTARG";;
	e) email="true";;
	q) qos="$OPTARG";;
	s) short="true";;
	S) submit="true";;
	t) touchfile="true";;
	D) depends="$OPTARG"; depjob="true";;
	C) files2copy+=($OPTARG);;
	:) echo "missing argument for option -$OPTARG"; print_usage; exit 1;;
	\?) echo "unknown option -$OPTARG"; print_usage; exit 1;;
	*) print_usage; exit 0;;
  esac
done

for var in $@
	do
	case ${var: -3} in
	".in") inp="psi4";;
	"inp") inp="orca";;
	"gjf") inp="gaussian";;
	*)     inp="none";;
	esac

	if [[ $inp != "none" ]]; then
		FULLFILEPATH=`readlink -f $var`
		FILEPATH=`dirname "$FULLFILEPATH"`

		case $inp in
		"psi4")
			PROCS=`cat "$FULLFILEPATH" | grep set_num_threads | cut -d'(' -f2 | cut -d')' -f1`
			MEM=`cat "$FULLFILEPATH" | grep memory | cut -d' ' -f2| cut -d'G' -f1`
			FILENAME=`/bin/basename -s .in "$FULLFILEPATH"`
			;;
		"orca")
			PROCS=`cat "$FULLFILEPATH" | grep nprocs | xargs | cut -d' ' -f2`
			MEM=`cat "$FULLFILEPATH" | grep maxcore | cut -d' ' -f2`
			MEM=$(($MEM * $PROCS))
			MEM=`echo $MEM | python -c "print(int(round(float(input())/1024)))"`
			FILENAME=`/bin/basename -s .inp "$FULLFILEPATH"`
			;;
		"gaussian")
			PROCS=`cat "$FULLFILEPATH" | grep -i nprocs | cut -d'=' -f2`
			MEM=`cat "$FULLFILEPATH" | grep mem | cut -d'=' -f2 | cut -d'G' -f1`
			FILENAME=`/bin/basename -s .gjf "$FULLFILEPATH"`
			;;
		esac

		if [[ $short == "true" ]]; then
			if [[ `hostname` == 'monarch'* ]]; then
				TIMESTRING="24:00:00"
				HOURS=24
			elif [[ `hostname` == 'm3'* ]]; then
				TIMESTRING="00:30:00"
				HOURS=0
				if [[ $qos == "none" ]]; then
					qos="shortq"
				else
					qos="${qos},shortq"
				fi
				if [[ $part == "none" ]]; then
					part="short"
				else
					part="${part},short"
				fi
			fi
		else
			if [[ $days == "none" ]]; then
				if [[ $hours == "none" ]]; then
					HOURS=24
					TIMESTRING="24:00:00"
				else
					HOURS=$hours
					TIMESTRING="${hours}:00:00"
				fi
			else
				HOURS=$(($days * 24))
				TIMESTRING="${HOURS}:00:00"
			fi
		fi


		if [[ $mem != "none" ]]; then
			MEM="$mem"
		fi

		if [[ $procs != "none" ]]; then
			PROCS="$procs"
		fi

		if [[ $tpn != "none" ]]; then
			TPN="$tpn"
		else
			TPN="$PROCS"
		fi


		if [[ `hostname` == 'monarch'* ]]; then
			SCRATCH="/home/$USER/scratch"
			ACCOUNT="p2015120004"
			PROJECT="/mnt/lustre/projects/$ACCOUNT"
			HOMEPATH="$PROJECT/$USER"
		elif [[ `hostname` == 'm3'* ]]; then
			ACCOUNT="sn29"
			SCRATCH="/home/$USER/${ACCOUNT}_scratch/$USER"
			PROJECT="/projects/$ACCOUNT"
			HOMEPATH="$PROJECT/$USER"
		fi

		echo "#!/bin/bash "																		> "$FILEPATH/$FILENAME.slm"
		echo "#SBATCH --time=$TIMESTRING"														>> "$FILEPATH/$FILENAME.slm"
		echo "#SBATCH --ntasks=$PROCS"															>> "$FILEPATH/$FILENAME.slm"
		echo "#SBATCH --cpus-per-task=1"														>> "$FILEPATH/$FILENAME.slm"
		echo "#SBATCH --ntasks-per-node=$TPN"													>> "$FILEPATH/$FILENAME.slm"
		echo "#SBATCH --mem=${MEM}GB"															>> "$FILEPATH/$FILENAME.slm"

		#email notifications
		if [[ $email == true ]]; then
			echo "#SBATCH --mail-type=ALL --mail-user=$EMAIL"									>> "$FILEPATH/$FILENAME.slm"
		fi

		#partition selection
		if [[ `hostname` == 'monarch'* ]]; then
			if [[ $part != "none" ]]; then
				if [[ $HOURS -le 24 ]]; then
					echo "#SBATCH --partition=comp,short,$part" 								>> "$FILEPATH/$FILENAME.slm"
				fi
				echo "#SBATCH --partition=comp,$part" 											>> "$FILEPATH/$FILENAME.slm"
			else
				if [[ $HOURS -le 24 ]]; then
					echo "#SBATCH --partition=comp,short" 										>> "$FILEPATH/$FILENAME.slm"
				else
					echo "#SBATCH --partition=comp" 											>> "$FILEPATH/$FILENAME.slm"

				fi
			fi
		elif [[ `hostname` == 'm3'* ]]; then
			if [[ $part != "none" ]]; then
				echo "#SBATCH --partition=$part" 												>> "$FILEPATH/$FILENAME.slm"
			fi
			echo "#SBATCH --account=$ACCOUNT"													>> "$FILEPATH/$FILENAME.slm"

		fi
		HOURS=`printf "%02d\n" $HOURS` 

		#qos selection
		if [[ $qos != "none" ]]; then
			if [[ `hostname` == 'monarch'* ]]; then
				echo "#SBATCH --qos=partner,$qos"												>> "$FILEPATH/$FILENAME.slm"
			else
				echo "#SBATCH --qos=$qos"														>> "$FILEPATH/$FILENAME.slm"
			fi
		else
			if [[ `hostname` == 'monarch'* ]]; then
				echo "#SBATCH --qos=partner"													>> "$FILEPATH/$FILENAME.slm"
			fi
		fi
		echo ""																					>> "$FILEPATH/$FILENAME.slm"
		echo "export PROJECT=\"$ACCOUNT\""														>> "$FILEPATH/$FILENAME.slm"

		case $inp in
		"psi4")
			echo "module load psi4/v1.3.2"														>> "$FILEPATH/$FILENAME.slm"
			echo "export PSI_SCRATCH=\"$SCRATCH/$FILENAME\""									>> "$FILEPATH/$FILENAME.slm"
			echo "export PSIPATH=\$PSIPATH:$HOMEPATH/basis-sets/psi4"							>> "$FILEPATH/$FILENAME.slm"
			setupscratch
			copyfiles
			echo "psi4 -i \"$FILENAME.in\" -o \"$FILEPATH/$FILENAME.out\" 2>&1"					>> "$FILEPATH/$FILENAME.slm"
			copyscratch

			;;
		"orca")
			echo "module unload orca/4.2.1"														>> "$FILEPATH/$FILENAME.slm"
			echo "module load orca/4.2.1-216"													>> "$FILEPATH/$FILENAME.slm"
			setupscratch	
			copyfiles
			echo "\$ORCA_ROOT/orca \"$FILENAME.inp\" > \"$FILEPATH/$FILENAME.out\" 2>&1"		>> "$FILEPATH/$FILENAME.slm"
			copyscratch

			;;
	
		# "gaussian")
		# 	echo "module load gaussian/g16a03"													>> "$FILEPATH/$FILENAME.slm"
		# 	echo "SCRATCHDIR=\"$SCRATCH/$FILENAME\""											>> "$FILEPATH/$FILENAME.slm"
		# 	echo ""																				>> "$FILEPATH/$FILENAME.slm"
		# 	echo "mkdir \"$SCRATCH/$FILENAME\""													>> "$FILEPATH/$FILENAME.slm"
		# 	echo "mkdir \"$FILEPATH/$FILENAME\""												>> "$FILEPATH/$FILENAME.slm"
		# 	echo "time G16 << END > \"$FILENAME.out\" 2>&1"										>> "$FILEPATH/$FILENAME.slm"
		# 	cat $FULLFILEPATH																	>> "$FILEPATH/$FILENAME.slm"
		# 	echo ""																				>> "$FILEPATH/$FILENAME.slm"
		# 	echo "END"																			>> "$FILEPATH/$FILENAME.slm"
		# 	echo ""																				>> "$FILEPATH/$FILENAME.slm"
		# 	;;
		
		"gaussian")
			echo "module load gaussian/g16a03"													>> "$FILEPATH/$FILENAME.slm"
			echo ""																				>> "$FILEPATH/$FILENAME.slm"
			echo "cat \"$FULLFILEPATH\" | G16 > \"$FILEPATH/$FILENAME.out\" 2>&1"				>> "$FILEPATH/$FILENAME.slm"
			;;
		esac

		if [[ $touchfile == "true" ]]; then
			touch "$FILEPATH/$FILENAME.out"
		fi

		~/bin/dos2unix "$FILEPATH/$FILENAME.slm"

		if [[ $depjob == "true" ]]; then
			depcommand="-d afterany:${depends}"
		fi

		if [[ $submit == "true" ]]; then
			cd "$FILEPATH"
			sbatch $depcommand "$FILEPATH/$FILENAME.slm"
			cd "$DIR"
		fi
	fi
done
