#!/usr/bin/bash

#SBATCH -J deltaK_large=0.2
#SBATCH -N 1
#SBATCH -p tyhcnormal
#SBATCH --ntasks-per-node=64
#SBATCH --cpus-per-task=1

ulimit -s unlimited
ulimit -l unlimited

# load the environment
module purge
source /work/home/jyzhang/apprepo/lammps/stable.29Aug2024-intelmpi2021/scripts/env.sh
export UCX_IB_ADDR_TYPE=ib_global
export I_MPI_PMI_LIBRARY=/opt/gridview/slurm/lib/libpmi.so

delta_K=0.1
K_0=0.5
delta_K_large=0.2

outlog="log/out.$index-$Temp"

if [ -f "$outlog" ]; then
    rm "$outlog"
fi

record="txt/$index-${Temp}.txt"

if [ -f "$record" ]; then
    rm "$record"
    echo "step K" >> $record
fi

echo "~~~~~~~*******~~~~~~" >> $outlog
echo "Submitting job: Temp=$Temp, index=$index, K_final=$K_final" >> $outlog
echo >> $outlog
#--------------- generate initial data at T ---------------

ini_data="config/dynamic/Mo_${index}_${Temp}.data"

if [ ! -f "$ini_data" ]; then
    srun --mpi=pmix_v3 lmp_mpi -var T ${Temp} -var idx ${index} -in in.crack1-aniso-ini

    if [[ $? -ne 0 ]]; then
        echo "????????????????" >> $outlog
        echo "Initiaization failed!!!" >> $outlog
        echo "????????????????" >> $outlog
        exit 2
    fi

    echo "Generated the initial configuration at temperature $Temp with K=0." >> $outlog
    echo >> $outlog
else
    echo "The initial configuration at temeprature $Temp with K=0 exits." >> $outlog
    echo >> $outlog
fi


dir="dump/${index}"

if [ ! -d "$dir" ]; then
    mkdir "$dir"
else
    rm -rf "${dir}/*"
fi

cp    $ini_data dump/${index}/Mo_${index}_${Temp}_0_eq.data

# ------------- Apply K incrementally ---------------
now_step=0
flag=1
if (( $(echo "$K_final < $K_0" | bc -l) )); then 
    dK1=$delta_K
    max_iter1=$(echo "$K_final / $dK1" | bc)
    echo "maxiter1: $max_iter1" >> $outlog
    echo >> $outlog
    flag=0
else
    dK1=$delta_K_large
    dK2=$delta_K
    max_iter1=$(echo "$K_0 / $dK1" | bc)
    max_iter2=$(echo "($K_final - $K_0) / $dK2 + $max_iter1" | bc)
    echo "maxiter1: $max_iter1" >> $outlog 
    echo "maxiter2: $max_iter2" >> $outlog
    echo >> $outlog
fi

echo "Start to apply K incrementally..." >> $outlog

while [[ $now_step -lt $max_iter1 ]]; do
    python displace.py ${index} ${Temp} ${dK1} ${now_step}

    ((now_step++))
    now_K=$(echo "$dK1 * $now_step" | bc)
    echo "$now_step $now_K" >> $record 
    echo "===============================" >> $outlog
    echo "now_step: $now_step" >> $outlog
    echo "now_K: $now_K" >> $outlog

    if [[ $? -ne 0 ]]; then
        echo "????????????????" >> $outlog
	echo "Displace atoms failed!!!" >> $outlog
        echo "????????????????" >> $outlog
	echo >> $outlog
	exit 3
    else
        echo "Displace atoms finished!!!" >> $outlog
	echo >> $outlog
    fi
    
    srun --mpi=pmix_v3 lmp_mpi -var T ${Temp} -var idx ${index} -var now_step ${now_step}  -in in.crack1-aniso-rlx

    if [[ $? -ne 0 ]]; then
        echo "????????????????" >> $outlog
	echo "Relaxation failed!!!" >> $outlog
        echo "????????????????" >> $outlog
	echo >> $outlog
	exit 4
    else
        echo "Relaxation finished!!!" >> $outlog
	echo >> $outlog
    fi
    
done

if [[ $flag -eq 1 ]]; then
    while [[ $now_step -lt $max_iter2 ]]; do
        python displace.py ${index} ${Temp} ${dK2} ${now_step}

        ((now_step++))
        now_K=$(echo "$now_K + $dK2" | bc)
        echo "$now_step $now_K" >> txt/$index-$Temp.txt
            echo "===============================" >> $outlog
        echo "now_step: $now_step" >> $outlog
        echo "now_K: $now_K" >> $outlog

        if [[ $? -ne 0 ]]; then
            echo "????????????????" >> $outlog
            echo "Displace atoms failed!!!" >> $outlog
                echo "????????????????" >> $outlog
            echo >> $outlog
            exit 3
        else
                echo "Displace atoms finished!!!" >> $outlog
            echo >> $outlog
        fi
    
    	srun --mpi=pmix_v3 lmp_mpi -var T ${Temp} -var idx ${index} -var now_step ${now_step}  -in in.crack1-aniso-rlx

    	if [[ $? -ne 0 ]]; then
            echo "????????????????" >> $outlog
    	    echo "Relaxation failed!!!" >> $outlog
            echo "????????????????" >> $outlog
	        echo >> $outlog
	        exit 4
    	else
            echo "Relaxation finished!!!" >> $outlog
	        echo >> $outlog
    	fi
    
    done
fi
echo "Finished job: Temp=$Temp, index=$index, K_final=$K_final" >> $outlog
echo "~~~~~~~*******~~~~~~" >> $outlog

