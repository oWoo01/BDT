# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : ddplot.py
# Time       ：2025/7/7 21:23
# Author     ：oWoo
# Description：compute dd
# Source     : https://www.ctcms.nist.gov/potentials/atomman/tutorial/4.10_Differential_Displacement_Maps.html
"""


# Standard Python libraries
from copy import deepcopy
import datetime

# http://www.numpy.org/
import numpy as np

# https://matplotlib.org/
import matplotlib.pyplot as plt

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

import sys
import glob
import re

def read_box_half(filename):

    xlo = xhi = ylo = yhi = None
    with open(filename, 'r') as f:
        for line in f:
            if 'xlo xhi' in line:
                vals = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                xlo, xhi = map(float, vals)
            elif 'ylo yhi' in line:
                vals = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                ylo, yhi = map(float, vals)
            if xlo is not None and ylo is not None:
                break
    if None in (xlo, xhi, ylo, yhi):
        raise ValueError("Could not fine xlo/xhi or ylo/yhi")
    xhalf = (xhi + xlo) / 2
    yhalf = (yhi + ylo) / 2
    return xhalf, yhalf

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(f"Usage: python {sys.argv[0]} <file_perf> <file_disl> <lc> <elem>")
        sys.exit(1)
    file_base = sys.argv[1]
    file_disl =  sys.argv[2]
    lc = float(sys.argv[3])
    elem = sys.argv[4]


    # Load dislocation configurations that were previously constructed using Dislocation class
    base_system = am.load('atom_data', file_base)
    disl_system = am.load('atom_data', file_disl)
    alat = uc.set_in_units(lc, 'Å')
    burgers = np.array([0.0, 0.0, alat / 2 * np.sqrt(3)])

    xhalf, yhalf = read_box_half(file_base)
    xlim_l = xhalf - 2 * lc
    xlim_r = xhalf + 2 * lc
    ylim_l = yhalf - 2 * lc
    ylim_r = yhalf + 2 * lc

    base_neighbors = base_system.neighborlist(cutoff=0.9 * alat)
    disl_neighbors = disl_system.neighborlist(cutoff=0.9 * alat)

    dd = am.defect.DifferentialDisplacement(base_system, disl_system, neighbors=base_neighbors, reference=0)        # reference as the base configuration
    # dd = am.defect.DifferentialDisplacement(base_system, disl_system, neighbors=disl_neighbors, reference=1)      # reference as on the dislocation configuration

    # dd.ddvectors: computed dd vectors for each pair of atoms
    # dd.arrowcenters : center position for each of the vector arrows (midpoints between the atom pair)
    # dd.arrowuvectors: unit vectors associated with the relative position vectors for each pair of neighbor atoms.

    # Create dict of common plotting parameter values for all
    params = {}
    params['ddmax'] = np.linalg.norm(burgers) / 2  # Use |b|/2 for full dislocation
    params['plotxaxis'] = 'x'  # perpendicular to dislocation line in slip surface
    params['plotyaxis'] = 'y'  # slip surface
    params['figsize'] = 10  # Plots will be "regular" if only one size value is given

    params['xlim'] = (xlim_l, xlim_r)  # Plotting limits for the plotting x-axis.  Large as this is along the slip plane
    params['ylim'] = (ylim_l, ylim_r)  # Plotting limits for the plotting y-axis.  Small as this is perpendicular to the slip plane
    params['zlim'] = (8, alat * 3 ** 0.5 +8)  # Should be one periodic length of the crystal along the dislocation line direction

    params['atomcmap'] = 'gray'

    dd.plot('z', **params)
    plt.savefig('ddmap.png', dpi=600)

