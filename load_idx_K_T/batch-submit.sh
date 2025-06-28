#!/usr/bin/bash

Temp_array=(300)
index_array=(1)
K_final_array=(1) # units:MPa*sqrt(m)

for i in ${!index_array[@]}; do
    index=${index_array[$i]}
    for j in ${!Temp_array[@]}; do
        Temp=${Temp_array[$j]}
        for k in ${!K_final_array[@]}; do
            K_final=${K_final_array[$k]}
            echo "$index $Temp $K_final"
            sbatch --job-name="crack-${index}-${Temp}-${K_final}" \
                   --output="log/log.$index-$Temp" \
                   --export=ALL,Temp=$Temp,index=$index,K_final=$K_final submit.sh
        done
    done
done
