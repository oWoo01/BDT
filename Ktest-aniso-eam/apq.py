# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : CS tensor.py
# Time       ：2025/6/13 17:06
# Author     ：oWoo
# Description：Read crack systems from Excel, rotate cubic stiffness tensor,
#              compute stiffness (C), compliance (S), and extract a1, a2, p1, p2, q1, q2.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Voigt notation mappings
voigt_pairs = {
    0: (0, 0),
    1: (1, 1),
    2: (2, 2),
    3: (1, 2),
    4: (0, 2),
    5: (0, 1)
}

# Factor for symmetric tensor -> Voigt
factor = np.array([1, 1, 1, 2, 2, 2])


def voigt_to_tensor_C(C_voigt):
    C_tensor = np.zeros((3, 3, 3, 3))
    for I in range(6):
        for J in range(6):
            i, j = voigt_pairs[I]
            k, l = voigt_pairs[J]
            value = C_voigt[I, J]
            C_tensor[i, j, k, l] = value
            C_tensor[j, i, k, l] = value
            C_tensor[i, j, l, k] = value
            C_tensor[j, i, l, k] = value
    return C_tensor

def tensor_to_voigt_C(C_tensor):
    C_voigt = np.zeros((6, 6))
    for I in range(6):
        i, j = voigt_pairs[I]
        for J in range(6):
            k, l = voigt_pairs[J]
            C_voigt[I, J] = 0.25 * (
                    C_tensor[i, j, k, l] + C_tensor[j, i, k, l] +
                    C_tensor[i, j, l, k] + C_tensor[j, i, l, k]
            )
    return C_voigt

# Rotate the stiffness tensor
def rotate_stiffness_tensor(C_voigt, R):
    C_tensor = voigt_to_tensor_C(C_voigt)
    C_rot = np.einsum('ia,jb,kc,ld,abcd->ijkl', R, R, R, R, C_tensor)
    C_voigt_rot = tensor_to_voigt_C(C_rot)
    return C_voigt_rot

# Normalize and create rotation matrix
def normalize(v):
    return v / np.linalg.norm(v)


def c_to_s(C_voigt):
    C11 =C_voigt(0, 0)
    C12 = C_voigt(0, 1)
    C44 = C_voigt(3, 3)
    S11 = (C11+C12)/(C11-C12)/(C11+2*C12)
    S12 = -C12/(C11-C12)/(C11+2*C12)
    S44 = 1/C44
    S_voigt = np.array([
        [S11, S12, S12, 0, 0, 0],
        [S12, S11, S12, 0, 0, 0],
        [S12, S12, S11, 0, 0, 0],
        [0, 0, 0, S44, 0, 0],
        [0, 0, 0, 0, S44, 0],
        [0, 0, 0, 0, 0, S44]
    ])
    return S_voigt

def extract_Sp(S):
    # 提取 S^p_ij = S_ij - S_i3*S_3j / S_33
    Sp = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            Sp[i, j] = S[i, j] - S[i, 2] * S[2, j] / S[2, 2]
    Sp16 = S[0, 5] - S[0, 2] * S[2, 5] / S[2, 2]
    Sp26 = S[1, 5] - S[1, 2] * S[2, 5] / S[2, 2]
    Sp66 = S[5, 5] - S[5, 2] * S[2, 5] / S[2, 2]
    return Sp, Sp16, Sp26, Sp66

def solve_characteristic_eq(Sp11, Sp12, Sp22, Sp16, Sp26, Sp66):
    coeffs = [Sp11,
              -2 * Sp16,
              2 * Sp12 + Sp66,
              -2 * Sp26,
              Sp22]
    roots = np.roots(coeffs)
    return roots

def compute_pq(Sp, Sp16, Sp26, a1, a2):
    Sp11, Sp12, Sp22 = Sp[0, 0], Sp[0, 1], Sp[1, 1]
    p1 = Sp11 * a1**2 + Sp12 - Sp16 * a1
    p2 = Sp11 * a2**2 + Sp12 - Sp16 * a2
    q1 = Sp22 / a1 + Sp12 * a1 - Sp26
    q2 = Sp22 / a2 + Sp12 * a2 - Sp26
    return p1, p2, q1, q2


def process(input, output, apq_output, C11, C12, C44):
    df = pd.read_excel(input)

    # Define initial cubic stiffness matrix
    C_cubic = np.array([
        [C11, C12, C12, 0, 0, 0],
        [C12, C11, C12, 0, 0, 0],
        [C12, C12, C11, 0, 0, 0],
        [0, 0, 0, C44, 0, 0],
        [0, 0, 0, 0, C44, 0],
        [0, 0, 0, 0, 0, C44]
    ])
    S = []

    with open(output, 'w') as f1, open(apq_output, 'w') as f2:
        for idx, row in df.iterrows():
            system_id = int(row['No.'])

            a = normalize(np.array([row['a1'], row['a2'], row['a3']]))
            b = normalize(np.array([row['b1'], row['b2'], row['b3']]))
            c = normalize(np.array([row['c1'], row['c2'], row['c3']]))

            R = np.vstack([a, b, c]).T
            C_rot = rotate_stiffness_tensor(C_cubic, R)
            S_rot = np.linalg.inv(C_rot)
            S.append(S_rot)

            f1.write(f"System {system_id}:\n")
            f1.write("C_rotated (GPa):\n")
            for line in C_rot:
                f1.write("  " + "  ".join(f"{v:10.4f}" for v in line) + "\n")

            f1.write("S_rotated (1/GPa):\n")
            for line in S_rot:
                f1.write("  " + "  ".join(f"{v:10.6f}" for v in line) + "\n")

            f1.write("\n" + "=" * 60 + "\n\n")

            Sp, Sp16, Sp26, Sp66 = extract_Sp(S_rot)
            a_roots = solve_characteristic_eq(Sp[0, 0], Sp[0, 1], Sp[1, 1], Sp16, Sp26, Sp66)
            positive_a_roots = [root for root in a_roots if root.imag > 0]
            a1, a2 = positive_a_roots[0], positive_a_roots[1]
            p1, p2, q1, q2 = compute_pq(Sp, Sp16, Sp26, a1, a2)

            f2.write(f"System {system_id}:")
            f2.write(f"\na1 = {a1.real:.6f} + {a1.imag:.6f}j")
            f2.write(f"\na2 = {a2.real:.6f} + {a2.imag:.6f}j")
            f2.write(f"\np1 = {p1.real:.6f} + {p1.imag:.6f}j")
            f2.write(f"\np2 = {p2.real:.6f} + {p2.imag:.6f}j")
            f2.write(f"\nq1 = {q1.real:.6f} + {q1.imag:.6f}j")
            f2.write(f"\nq2 = {q2.real:.6f} + {q2.imag:.6f}j")
            f2.write("\n" + "-" * 50 + "\n")
    return S

if __name__ == '__main__':
    C11 = 423.283   # unit: GPa
    C12 = 143.104
    C44 = 95.474

    filepath = '/Users/kaioneer/Documents/A-Research/BDT'
    input = f'{filepath}/crack systems.xlsx'
    output = f'/Users/kaioneer/Documents/BDT data/properties/2012--Park-H-Fellinger-M-R-Lenosky-T-J-et-al--Mo/CS-Park_MEAM_Mo_2012.spline.txt'
    apq_output = f'/Users/kaioneer/Documents/BDT data/properties/2012--Park-H-Fellinger-M-R-Lenosky-T-J-et-al--Mo/apq-Park_MEAM_Mo_2012.spline.txt'
    S = process(input, output, apq_output, C11, C12, C44)

    # compute theoretical fracture toughness according to the Griffith concept
    gammas = list(pd.read_excel(input)['surface energy (J/m2)'])    # unit: J/m2

    K_I = []
    for i in range(len(gammas)):
        Si = S[i]
        G_I = 2 * gammas[i]

        S11 = Si[0,0]   # unit: 1/GPa
        S22 = Si[1,1]
        S33 = Si[2,2]
        S13 = Si[0,2]
        S12 = Si[0,1]
        S23 = Si[1,2]
        S66 = Si[5,5]
        S26 = Si[1,5]

        b11 = (S11*S33 - S13**2) / S33
        b22 = (S22*S33 - S23**2) / S33
        b12 = (S12*S33 - S13*S23) / S33
        b66 = (S66*S33 - S26**2) / S33
        B = np.sqrt(b11*b22/2 * (np.sqrt(b22/b11) + (2*b12+b66)/2/b11))

        Ki = np.sqrt(G_I/B)*0.1     # unit: MPa/sqrt(m)
        K_I.append(Ki)
