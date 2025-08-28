#!/usr/bin/bash

Temp_array=(300) 
index_array=(3)
K_final_array=(0.2) # units:MPa*sqrt(m)

for i in ${!index_array[@]}; do
    index=${index_array[$i]}
    Temp=${Temp_array[$i]}
    K_final=${K_final_array[$i]}
    echo "$index $Temp $K_final"

    dir="dump/${index}/${Temp}"

    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
    else
        find "$dir" -mindepth 1 -delete
    fi

    sbatch --job-name="crack-${index}-${Temp}-${K_final}" \
           --output="${dir}/A-log.$index-$Temp" \
           --export=ALL,Temp=$Temp,index=$index,K_final=$K_final submit.sh
done
