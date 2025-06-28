# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : displace.py
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

def displace_atoms(fin, fout, dK, coeff):
    a1 = coeff[0]
    a2 = coeff[1]
    p1 = coeff[2]
    p2 = coeff[3]
    q1 = coeff[4]
    q2 = coeff[5]

    flag = True

    with open(fin, 'r') as f1, open(fout, 'w') as f2:
        for i, line in enumerate(f1, 1):
            if i < 19:
                f2.write(line)
                if 'ylo yhi' in line:
                    parts = line.split()[:2]
                    ylo, yhi = float(parts[0]), float(parts[1])
                    yhalf = (ylo + yhi) / 2
                elif 'zlo zhi' in line:
                    parts = line.split()[:2]
                    zlo, zhi = float(parts[0]), float(parts[1])
                    zhalf = (zlo + zhi) / 2
            else:
                if line.strip() == "":
                    flag = False     # flag = True, this line refers to the position of atom.

                if flag:
                    parts = line.split()
                    atom_type = parts[1]

                    if atom_type == '4':         # This atom is in the boundary
                        y = float(parts[3])
                        z = float(parts[4])

                        dy = y - yhalf
                        dz = z - zhalf
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
        print("  python displace.py system_index temperature delta_K step")
        sys.exit(1)

    idx = int(sys.argv[1])
    T = int(sys.argv[2])
    dK = float(sys.argv[3]) * 100000  # m^1/2 to Å^1/2
    step = int(sys.argv[4])

    print(idx, T, dK, step)

    try:
        coeff = parse_system_data('properties/apq-mo.fs.eam.alloy.txt', idx)
        old_datafile = f'dump/{idx}/Mo_{idx}_{T}_{step}_eq.data'

        step += 1

        new_datafile = f'dump/{idx}/Mo_{idx}_{T}_{step}.data'
        displace_atoms(old_datafile, new_datafile, dK, coeff)

    except FileNotFoundError:
        print(f"Error: Input file not found")
    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")


