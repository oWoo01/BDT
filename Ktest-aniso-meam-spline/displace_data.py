# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : displace_data.py
# Time       ：2025/6/25 09:56
# Author     ：oWoo
# Description：Apply displacement increments corresponding to stress intensity factor increment
# Input: system index, T, delta_K (units: MPa*m^1/2), step
"""
import numpy as np
import sys
import cmath
import re
import math


def parse_system_data(filename, index):
    with open(filename, 'r') as f:
        content = f.read()

    systems = re.split(r'-{10,}', content.strip())

    if index < 1 or index > len(systems):
        raise ValueError("System index out of range.")

    system_text = systems[index - 1]

    def extract_value(name):
        pattern = rf'{name} = ([\d\.\+\-eE]+) \+ ([\d\.\+\-eE]+)j'
        match = re.search(pattern, system_text)
        if not match:
            raise ValueError(f"{name} not found in System {index}")
        real = float(match.group(1))
        imag = float(match.group(2))
        return complex(real, imag)

    a1 = extract_value('a1')
    a2 = extract_value('a2')
    p1 = extract_value('p1') / 1000     # 1/GPa -> 1/MPa
    p2 = extract_value('p2') / 1000
    q1 = extract_value('q1') / 1000
    q2 = extract_value('q2') / 1000

    return a1, a2, p1, p2, q1, q2

def displace_atoms(forg, fin, fout, dK, coeff):
    a1, a2, p1, p2, q1, q2 = coeff

    flag = True
    with open(forg, 'r') as f0:
        lines0 = f0.readlines()
        ylo = float(lines0[6].strip().split()[0])
        yhi = float(lines0[6].strip().split()[1])
        zlo = float(lines0[7].strip().split()[0])
        zhi = float(lines0[7].strip().split()[1])
        yhalf = (ylo + yhi) / 2
        zhalf = (zlo + zhi) / 2
        ntotal = int(lines0[2].strip().split()[0])
        atoms = lines0[15:15 + ntotal]
        id2coord0 = {int(a.strip().split()[0]): (float(a.strip().split()[3]), float(a.strip().split()[4])) for a in atoms}

    with open(fin, 'r') as f1:
        lines1 = f1.readlines()
        ntotal1 = int(lines1[2].strip().split()[0])
        if ntotal1 != ntotal:
            raise ValueError("Number of atoms in the two files do not match.")

    with open(fout, 'w') as f2:
        for i, line in enumerate(lines1):
            
            if i < 15:
                f2.write(line)
            else:
                if line.strip() == "":
                    print(i, "Empty line")
                    flag = False     # flag = True, this line refers to the position of atom.

                if flag:
                    print(i)
                    parts = line.split()
                    atom_id = int(parts[0])
                    atom_type = lines1[i + 2 * (ntotal + 3)].strip().split()[1]       

                    if atom_type == '4':         # This atom is in the boundary
                        y = float(parts[3])
                        z = float(parts[4])

                        y0 = id2coord0[atom_id][0]
                        z0 = id2coord0[atom_id][1]

                        dy = y0 - yhalf
                        dz = z0 - zhalf
                        r = np.sqrt(dy**2 + dz**2)
                        theta = math.atan2(dz, dy)

                        term1 = a1 * p2 * cmath.sqrt(np.cos(theta) + a2 * np.sin(theta))
                        term2 = a2 * p1 * cmath.sqrt(np.cos(theta) + a1 * np.sin(theta))
                        term3 = a1 * q2 * cmath.sqrt(np.cos(theta) + a2 * np.sin(theta))
                        term4 = a2 * q1 * cmath.sqrt(np.cos(theta) + a1 * np.sin(theta))

                        Cplx1 = (term1 - term2) / (a1 - a2)
                        Cplx2 = (term3 - term4) / (a1 - a2)
                        newy = y + dK * np.sqrt(2*r/math.pi) * Cplx1.real
                        newz = z + dK * np.sqrt(2*r/math.pi) * Cplx2.real

                        parts[3] = str(newy)
                        parts[4] = str(newz)

                        new_line = " ".join(parts) + "\n"
                        f2.write(new_line)
                    else:
                        f2.write(line)
                else:
                    f2.write(line)



if __name__ == '__main__':

    if len(sys.argv) != 5:
        print("Usage: python script.py <index> <T> <dK> <step>")
        print("Example:")
        print("  python displace_data.py system_index temperature delta_K step")
        sys.exit(1)

    idx = int(sys.argv[1])
    T = int(sys.argv[2])
    dK = float(sys.argv[3]) * 100000  # m^1/2 to Å^1/2
    step = int(sys.argv[4])

    print(idx, T, dK, step)

    try:
        coeff = parse_system_data('properties/apq-Park_MEAM_Mo_2012.spline.txt', idx)
        origin_datafile = f'dump/{idx}/{T}/Mo_{idx}_{T}_0_eq.data'
        old_datafile = f'dump/{idx}/{T}/Mo_{idx}_{T}_{step}_eq.data'

        step += 1

        new_datafile = f'dump/{idx}/{T}/Mo_{idx}_{T}_{step}.data'
        displace_atoms(origin_datafile, old_datafile, new_datafile, dK, coeff)

    except FileNotFoundError:
        print(f"Error: Input file not found")
    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")


