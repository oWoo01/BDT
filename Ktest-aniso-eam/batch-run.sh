#!/usr/bin/bash

Temp_array=(300 1600)
index_array=({1..7})
K_initial_array=(0)
K_final_array=(3) # units:MPa*sqrt(m)
dK=0.1
potential="eam-2018--Setyawan-W-Gao-N-Kurtz-R-J--W-Re"
p_name="WRe_Setyawan_set145.eam.alloy"

for i in ${!index_array[@]}; do
    index=${index_array[$i]}
    for j in ${!Temp_array[@]}; do
        Temp=${Temp_array[$j]}
        for k in ${!K_final_array[@]}; do
        	K_initial=${K_initial_array[$k]}
            K_final=${K_final_array[$k]}
            echo "$index $Temp $K_initial $K_final"
            sbatch --job-name="crack-${index}-${Temp}-2018" \
                   --output="${potential}/log/$index-$Temp-log" \
                   --export=ALL,Temp=$Temp,index=$index,K_initial=$K_initial,K_final=$K_final,dK=$dK,potential=$potential,p_name=$p_name submit.sh
        done
    done
done
