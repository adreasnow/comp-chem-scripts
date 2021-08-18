#!/bin/bash
DIR=`pwd`
print_usage() {
	echo """
	Usage: 2slm -d [DAYS] -h [HOURS] -s -m [MEM (GB)] -n [TPN]
	  -c [PROCS] -p [PARTITIONS] -e -q [QOS] -t -P -N -C [FILE1]
	  -C [FILE2] -D [JOBID] -V [SOFTWARE VERSION] [INPUT FILES]...

	Arguments
	  [FILE] the files to be converted into slurm fils

	MANDATORY ###############################################################
		 --if no time flag is set, the script will defalt to 24 hours--
		                    --only use one of these--

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

	  -V software version, choose from:
	  	For ORCA - 4 (ORCA 4.2.1) and 5 (ORCA 5.0.1) (default = 5)
		For Psi4 - 1.3 (Psi4 1.3.2) and 1.4 (Psi4 1.4.0) (default = 1.4)
			Assumes Psi4 is installed with Miniconda in psi4-1.4

	  -D SLURM dependency ('-d afterany:<JOBID>')

	  -P works from project directory instead of scratch (ORCA and Psi4 only)

	  -N (notify) This is an advanced feature that allows you to creat a webhook input at ifttt.com
	    and will send a request with the values 
	      - value1:job name
	      - value2:status (submitted/running/finished)
	      - value3:tail of log file where value2=status
	    This requires two environment variables (exported from your .rc file)
	      - JOBID which is the name of the ifttt webhook
	      - JOBKEY which contains your API key

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
		COPYFILEPATH=`realpath $var`
		echo "cp \"$COPYFILEPATH\" \"$SCRATCH/$FILENAME\""									>> "$FILEPATH/$FILENAME.slm"
	done
}

notifysubmit() {
	echo '{' 																			>> ./data.json
	echo '  "value1":"'$FILENAME'",'													>> ./data.json
	echo '  "value2":"submitted",' 														>> ./data.json
	echo '  "value3":""'																>> ./data.json
	echo '}' 																			>> ./data.json

	curl -s -X POST -H "Content-Type: application/json" -d "@data.json" https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null
	rm -rf ./data.json
}

echonotifystart() {
	echo """
echo '{' 																			>> ./data.json
echo '  \"value1\":\"$FILENAME\",'													>> ./data.json
echo '  \"value2\":\"running\",' 													>> ./data.json
echo '  \"value3\":\" \"'															>> ./data.json
echo '}' 																			>> ./data.json
curl -s -X POST -H \"Content-Type: application/json\" -d \"@data.json\" https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null
rm -rf ./data.json

""" >> "$FILEPATH/$FILENAME.slm"
}

echonotifyend() {
	echo """
cd \""$FILEPATH/$FILENAME"\"
echo '{' 																			>> ./data.json
echo '  \"value1\":\"$FILENAME\",'													>> ./data.json
echo '  \"value2\":\"finished\",' 													>> ./data.json
echo '  \"value3\":\" \"'															>> ./data.json
echo '}' 																			>> ./data.json
curl -s -X POST -H \"Content-Type: application/json\" -d \"@data.json\" https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null
rm -rf ./data.json

""" >> "$FILEPATH/$FILENAME.slm"
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
	projectdir="false"
	notify="false"
	orcaversion="5"
	psi4version="1.4"

while getopts 'V:h:m:n:c:p:d:tD:sSNePq:C:' flag "${@}"; do
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
	P) projectdir="true";;
	N) notify="true";;
	V) orcaversion="$OPTARG";psi4version="$OPTARG";;
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
	if [[ $inp == "orca" ]]; then 
		if [[ $orcaversion == "4" ]] || [[ $orcaversion == "5" ]]; then
			echo "Using ORCA version $orcaversion"
		else
			echo "ORCA version not recognised or supported"
			exit 0
		fi
	fi
	if [[ $inp == "psi4" ]]; then
		if [[ $psi4version == "1.3" ]] || [[ $psi4version == "1.4" ]]; then
			echo "Using Psi4 version $psi4version"
		else
			echo "Psi4 version not recognised or supported"
			exit 0
		fi
	fi

	if [[ $inp != "none" ]]; then
		FULLFILEPATH=`realpath $var`
		FILEPATH=`dirname "$FULLFILEPATH"`

		case $inp in
		"psi4")
			PROCS=`cat "$FULLFILEPATH" | grep set_num_threads | cut -d'(' -f2 | cut -d')' -f1`
			MEM=`cat "$FULLFILEPATH" | grep memory | cut -d' ' -f2| cut -d'G' -f1`
			FILENAME=`/bin/basename -s .in "$FULLFILEPATH"`
			;;
		"orca")
			PROCS=`cat "$FULLFILEPATH" | grep nprocs | xargs | cut -d' ' -f2 | sort -rn | head -n 1`
			MEM=`cat "$FULLFILEPATH" | grep maxcore | cut -d' ' -f2 | sort -rn | head -n 1`
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

		if [[ $notify == "true" ]]; then
			echonotifystart
		fi

		case $inp in
		"psi4")
			if [[ $psi4version == "1.3" ]]; then
				echo "module load psi4/v1.3.2" 													>> "$FILEPATH/$FILENAME.slm"
			elif [[ $psi4version == "1.4" ]]; then
				echo "source $PROJECT/apps/psi4-1.4/activate_psi4.sh" 							>> "$FILEPATH/$FILENAME.slm"
			fi

			echo "export PSIPATH=\$PSIPATH:$HOMEPATH/basis"										>> "$FILEPATH/$FILENAME.slm"

			if [[ $projectdir == "true" ]]; then
				echo "export export PSIPATH=\"PSIPATH:$PSIPATH\""								>> "$FILEPATH/$FILENAME.slm"
				echo "export PSI_SCRATCH=\"$FILEPATH/$FILENAME\""								>> "$FILEPATH/$FILENAME.slm"
				echo "mkdir \"$FILEPATH/$FILENAME\""											>> "$FILEPATH/$FILENAME.slm"
				echo "cp \"$FILEPATH/$FILENAME.inp\" \"$FILEPATH/$FILENAME\""					>> "$FILEPATH/$FILENAME.slm"
				echo "cd \"$FILEPATH/$FILENAME\""												>> "$FILEPATH/$FILENAME.slm"
				echo "psi4 -i \"$FILENAME.in\" -o \"$FILENAME.out\" 2>&1"						>> "$FILEPATH/$FILENAME.slm"
			else
				echo "export PSI_SCRATCH=\"$SCRATCH/$FILENAME\""								>> "$FILEPATH/$FILENAME.slm"
				setupscratch
				copyfiles
				echo "psi4 -i \"$FILENAME.in\" -o \"$FILEPATH/$FILENAME.out\" 2>&1"				>> "$FILEPATH/$FILENAME.slm"
				copyscratch
			fi
			;;
		"orca")
			if [[ $orcaversion == "5" ]]; then
				######################### For orca 5.0.1 #########################
				echo "source $PROJECT/apps/orca_5.0.1/activate_orca.sh"							>> "$FILEPATH/$FILENAME.slm"
			elif [[ $orcaversion == "4" ]]; then
				######################### For orca 4.2.1 #########################
				echo "module unload orca/4.2.1"													>> "$FILEPATH/$FILENAME.slm"
				echo "module load orca/4.2.1-216"												>> "$FILEPATH/$FILENAME.slm"
			fi

			MPIARGS="--mca btl_openib_warn_no_device_params_found 0 --mca pml ob1 --mca btl ^openib"
			if [[ $projectdir == "true" ]]; then
				echo "mkdir \"$FILEPATH/$FILENAME\""											>> "$FILEPATH/$FILENAME.slm"
				echo "cp \"$FILEPATH/$FILENAME.inp\" \"$FILEPATH/$FILENAME\""					>> "$FILEPATH/$FILENAME.slm"
				echo "cd \"$FILEPATH/$FILENAME\""												>> "$FILEPATH/$FILENAME.slm"
				echo "\$ORCA_ROOT/orca \"$FILENAME.inp\" \"$MPIARGS\" > \"$FILEPATH/$FILENAME.out\" 2>&1"	>> "$FILEPATH/$FILENAME.slm"
			else
				setupscratch	
				copyfiles
				echo "\$ORCA_ROOT/orca \"$FILENAME.inp\" \"$MPIARGS\" > \"$FILEPATH/$FILENAME.out\" 2>&1"	>> "$FILEPATH/$FILENAME.slm"
				copyscratch
			fi
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

		if [[ $notify == "true" ]]; then
			echonotifyend
		fi

		if [[ $touchfile == "true" ]]; then
			touch "$FILEPATH/$FILENAME.out"
		fi

		~/bin/dos2unix "$FILEPATH/$FILENAME.slm"

		if [[ $depjob == "true" ]]; then
			depcommand="-d afterany:${depends}"
		fi

		if [[ $submit == "true" ]]; then
			cd "$FILEPATH"
			sbatch $depcommand "$FILEPATH/$FILENAME.slm" && if [[ $notify == "true" ]]; then notifysubmit; fi
			cd "$DIR"
		fi
	fi
done