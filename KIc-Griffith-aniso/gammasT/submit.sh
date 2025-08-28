#!/usr/bin/bash

ori_arrays=(100 110 111)
T_arrays=(300 1600)

echo "zori temp(K) E0 E1 Es(eV/A2)" > gammasT.txt
for i in ${ori_arrays[@]}; do
    echo $i
    for j in ${T_arrays[@]}; do
        echo ${j}K
        mpiexec.openmpi -np 64 lmp_g++_openmpi -var ori $i -var T $j -in in.s
    done
done
