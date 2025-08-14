#!/usr/bin/bash

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
export PATH=$PATH:/work/home/jyzhang/bin/atomsk
source /work/home/jyzhang/apprepo/miniconda3/etc/profile.d/conda.sh
conda activate base

outlog="$potential/log/$index-$Temp-outlog"

if [ -f "$outlog" ]; then
    rm "$outlog"
fi

echo "~~~~~~~*******~~~~~~" >> $outlog
echo "Submitting job: Temp=$Temp, index=$index, K_initial=$K_initial, K_final=$K_final" >> $outlog
echo >> $outlog

record="$potential/log/$index-${Temp}-record"

if (( $(echo "$K_initial == 0" | bc -l) )); then
    if [ -f "$record" ]; then
        rm "$record"
    fi
    echo "step K" >> $record
    now_step=0
    now_K=0
    ini_data="$potential/config/dynamic/W_${index}_${Temp}.data"
    
    #--------------- generate initial data at T ---------------
    if [ ! -f "$ini_data" ]; then
        srun --mpi=pmix_v3 lmp_mpi -var T ${Temp} -var idx ${index} -var potential $potential -var p_name $p_name -in in.crack1-aniso-ini
    
        if [[ $? -ne 0 ]]; then
            echo "Initiaization failed!!!" >> $outlog
            exit 2
        fi
    
        echo "Generated the initial configuration at temperature $Temp with K=0." >> $outlog
        echo >> $outlog
    else
        echo "The initial configuration at temeprature $Temp with K=0 exits." >> $outlog
        echo >> $outlog
    fi 
    
    dir="$potential/dump/${index}/${Temp}"
    
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
    else
        rm -rf "${dir}/"*
    fi
    
    cp    $ini_data $dir/W_${index}_${Temp}_0_eq.data
elif [ -f "$record" ]; then
    now_step=$(awk -v k_init="$K_initial" '$2 == k_init {print $1}' "$record")
    now_K=$K_initial

    if [ -z "$now_step" ]; then
        echo "Error: No step found for K=$K_initial in $record" >> $outlog
        exit 1
    fi

    echo "Found K=$K_initial corresponding to step=$now_step" >> $outlog
fi

# ------------- Apply K incrementally ---------------
max_iter=$(echo "($K_final - $K_initial) / $dK + $now_step" | bc)
echo "maxiter: $max_iter" >> $outlog
echo >> $outlog

echo "Start to apply K incrementally..." >> $outlog

while [[ $now_step -lt $max_iter ]]; do
    python displace_dump.py ${index} ${Temp} ${dK} ${now_step} ${potential}
    status=$?

    ((now_step++))
    now_K=$(echo "scale=6; $dK + $now_K" | bc)
    echo "$now_step $now_K" >> $record 
    echo "===============================" >> $outlog
    echo "now_step: $now_step" >> $outlog
    echo "now_K: $now_K" >> $outlog

    datafile="$potential/dump/${index}/${Temp}/W_${index}_${Temp}_${now_step}.data"
    lmpfile="$potential/dump/${index}/${Temp}/W_${index}_${Temp}_${now_step}.lmp"

    if [[ $status -ne 0 ]]; then
	    echo "Displace atoms failed!!!" >> $outlog
	    echo >> $outlog
	    exit 3
    else
        echo "Displace atoms finished." >> $outlog
        atomsk $datafile $lmpfile
        if [[ $? -eq 0 ]]; then
            rm $datafile
            echo "Convert data format finised." >> $outlog
            echo >> $outlog
        else
            echo "Convert data format failed!!!" >> $outlog
            exit 4
        fi
    fi
    
    srun --mpi=pmix_v3 lmp_mpi -var T ${Temp} -var idx ${index} -var now_step ${now_step} -var potential $potential -var p_name $p_name -in in.crack1-aniso-rlx

    if [[ $? -ne 0 ]]; then
	    echo "Relaxation failed!!!" >> $outlog
	    echo >> $outlog
	    exit 4
    else
        echo "Relaxation finished." >> $outlog
        rm $lmpfile
	    echo >> $outlog
    fi
    
done

echo "Finished job: Temp=$Temp, index=$index, K_initial=$K_initial, K_final=$K_final" >> $outlog
echo "~~~~~~~*******~~~~~~" >> $outlog

