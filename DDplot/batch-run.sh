#!/usr/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh
conda activate myenv

elem_array=('Nb' 'Mo' 'Ta' 'W')
lc_array=('3.3' '3.147' '3.301' '3.165')

for i in "${!elem_array[@]}"; do
    elem="${elem_array[$i]}"
    lc="${lc_array[$i]}"

    path="/home/jyzhang/lammps/BDT/DDplot/potentials/$elem"
    echo "=========================="
    echo "Processing element: $elem"
    echo "=========================="
    cd "$path"

    mapfile -t lines < "$path/potential-list.txt"
    
    for line in "${lines[@]}"; do

        [[ -z "$line" || "$line" =~ ^# ]] && continue

        folder=$(echo "$line" | awk '{print $1}')
        cd ${folder}

        if [[ -f ddmap.png ]]; then
            echo "Detected $folder/ddmap.png already exists, skipping this folder."
            cd ..
            continue
        fi

        rm *.cfg
        rm log.lammps

        type=$(echo "$line" | awk '{print $2}')
        echo "Processing potential: $folder"

        if [[ "$type" == "meam" ]]; then
            file1=$(echo "$line" | awk '{print $3}')
            file2=$(echo "$line" | awk '{print $4}')
            mpiexec.openmpi -np 32 lmp_g++_openmpi -var type "$type" -var file1 "$file1" -var file2 "$file2" -var lc "$lc" -var elem ${elem} -in ../../../in.disl_generate >> "log.lammps"
        else
            file=$(echo "$line" | awk '{print $3}')
            mpiexec.openmpi -np 32 lmp_g++_openmpi -var type "$type" -var file "$file" -var lc "$lc" -var elem ${elem} -in ../../../in.disl_generate >> "log.lammps"
        fi

        cfg_files=()
        for f in *.cfg; do
            [[ ! -e "$f" ]] && continue
            num=$(echo "$f" | grep -oP "${elem}\K\d+(?=\.cfg)")
            if [[ -n "$num" && $((num % 100)) -ne 0 ]]; then
                cfg_files+=("$f")
            fi
        done

        IFS=$'\n' 
        cfg_files=($(printf "%s\n" "${cfg_files[@]}" | sort -V)) 

        if [[ ${#cfg_files[@]} -lt 2 ]]; then
            echo "There is not enough cfg files for $elem in $folder"
            exit 1
        fi

        file_base=$(echo "${cfg_files[0]}" | grep -oP "${elem}\d+(?=\.cfg$)")
        file_disl=$(echo "${cfg_files[1]}" | grep -oP "${elem}\d+(?=\.cfg$)")

        echo "Converted cfg files to lmp format for $file_base and $file_disl"        
        atomsk "${file_base}.cfg" "${file_base}.lmp"
        atomsk "${file_disl}.cfg" "${file_disl}.lmp"

        echo "Running ddplot for $file_base and $file_disl"
        python3 /home/jyzhang/lammps/BDT/DDplot/ddplot.py "${file_base}.lmp" "${file_disl}.lmp" "$lc" "$elem"
        
        rm *.cfg
        echo "Finished processing $folder ✌️✌️✌️"
        cd ..
    done 
done
