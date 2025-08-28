# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : process.py
# Time       ：2025/8/14 10:35
# Author     ：oWoo
# Description：Compute crack length and observe if the critical event happens using ovito;
"""

from ovito.io import import_file
from ovito.modifiers import ConstructSurfaceModifier
from ovito.modifiers import DislocationAnalysisModifier
import numpy as np
import os
import matplotlib.pyplot as plt
import sys

os.environ['OVITO_GUI_MODE'] = '0'

def measure_crack_length(input_file):

    pipeline = import_file(input_file)
    modifier1 = ConstructSurfaceModifier(method=ConstructSurfaceModifier.Method.AlphaShape, radius=2.7, smoothing_level=8, select_surface_particles=True)
    pipeline.modifiers.append(modifier1)

    data = pipeline.compute()

    bd_lf = min(data.particles.positions[:,1]) + 12  # 12Å buffer
    bd_rt = max(data.particles.positions[:,1]) - 12 
    bd_hi = max(data.particles.positions[:,2]) - 12  # 12Å buffer
    bd_lo = min(data.particles.positions[:,2]) + 12
    y_coords = data.particles.positions[:, 1]
    z_coords = data.particles.positions[:, 2]
    mask1 = ((y_coords >= bd_lf) & (y_coords <= bd_rt) & (z_coords >= bd_lo) & (z_coords <= bd_hi))
    mask2 = data.particles['Selection'] == 1
    surf_atoms = data.particles.positions[mask1 & mask2]
    
    if surf_atoms.size == 0:
        crack_length = 0
    else:
        coords = surf_atoms[:,1]
        crack_length = np.max(coords) - np.min(coords)
    return crack_length


def precracked_length(input_file):
    pipeline = import_file(input_file)
    data = pipeline.compute()
    ly = data.cell[1,1]
    pre_l  = ly / 2 - 40 - 12
    
    return pre_l 

def count_dislocation(input_file):
    pipeline = import_file(input_file)
    modifier = DislocationAnalysisModifier(input_crystal_structure=DislocationAnalysisModifier.Lattice.BCC)
    pipeline.modifiers.append(modifier)
    data = pipeline.compute()

    return len(data.dislocations.lines)

if __name__ == "__main__":
    
    potential = sys.argv[1]
    path = f'/work/home/jyzhang/bdt-W/{potential}'
    crack_systems = [i for i in range(1,8)]
    Temp = ['300', '1600']

    if not os.path.exists(path):
        print(f"Path {path} does not exist. Please check the directory.")
        exit(1)

    Kc_file = f'{path}/Kc.txt'
    os.makedirs(f'{path}/pic', exist_ok=True)
    
    with open(Kc_file, 'w') as kcfout:
        kcfout.write('crack-system Temp Kc event-type disl-count\n') 
        for i in crack_systems:
            for j in Temp:
                print("==========================")
                print(f"Processing system {i} at {j}K")

                record_file = f"{path}/log/{i}-{j}-record"
                if not os.path.exists(record_file):
                    print(f"Record file {record_file} does not exist. Skipping!!!")
                    continue

                new_record = f"{path}/log/[proc]{i}-{j}-record"
                flag_b = 0
                flag_d = 0
                with open(record_file, 'r') as fin, open(new_record, 'w') as fout:
                    fout.write('step K crack-length\n')
                    next(fin)

                    for line in fin:
                        step = line.split()[0]
                        K = line.split()[1]
                        datafile = f'{path}/dump/{i}/{j}/W_{i}_{j}_{step}_eq.data'

                        if not os.path.exists(datafile):
                            print(f"Data file {datafile} does not exist. Skipping step {step}!!!")
                            continue

                        if step == '1':
                            pre_l = precracked_length(datafile)
                        
                        l = measure_crack_length(datafile)
                        fout.write(f"{step} {K} {l:.5f}\n")

                        if flag_d == 0 and flag_b == 0:
                            if count_dislocation(datafile) > 0:
                                flag_d = 1
                                kc = K
                                event_type = 'disl-emission'
                                print(f"Dislocation emission detected at K={K}.")
                            elif (l - pre_l) > 2:
                                flag_b = 1
                                kc = K
                                event_type = 'cleavage'
                                print(f"Cleavage detected at K={K}.")

                    if kc is None:
                        print(f"No critical K found!")
                        kcfout.write(f"{i} {j} - no-event -\n")
                    final_dislocation_count = count_dislocation(datafile)
                    kcfout.write(f"{i} {j} {kc} {event_type} {final_dislocation_count}\n")

                print(f"Finished processing.")

                Ks = np.loadtxt(new_record, skiprows=1, usecols=1)
                crack_lengths = np.loadtxt(new_record, skiprows=1, usecols=2)
                
                plt.figure()
                plt.plot(Ks, crack_lengths, '-o')
                plt.minorticks_on()
                plt.xlabel(r'K ($\mathrm{MPa\sqrt{m}}$)')
                plt.ylabel('Crack Length (Å)')
                plt.axhline(y=pre_l, color='r', linestyle='--', label='precrack length')
                plt.axvline(x=float(kc), color='g', linestyle='--', label=f'{event_type}')
                plt.title(f'System {i} at {j}K')
                plt.legend()
                plt.savefig(f'{path}/pic/{i}-{j}.png')        
                print("Plot saved.")
