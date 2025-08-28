# NOTE: This script can be modified for different atomic structures, 
# units, etc. See in.elastic for more info.
#

# Define the finite deformation size. Try several values of this
# variable to verify that results do not depend on it.
variable up equal 1.5e-2
 
# metal units, elastic constants in GPa
units		metal
variable cfac equal 1.0e-4
variable cunits string GPa

# Define MD parameters
variable nevery equal 10                  # sampling interval
variable nrepeat equal 10                 # number of samples
variable nfreq equal ${nevery}*${nrepeat} # length of one average
variable nthermo equal ${nfreq}           # interval for thermo output
variable nequil equal 50*${nthermo}       # length of equilibration run
variable nrun equal 50*${nthermo}          # length of equilibrated run
variable temp equal 300.0       # temperature of initial sample
variable timestep equal 0.001             # timestep
variable mass1 equal 183.84                # mass
variable adiabatic equal 2                # adiabatic (1) or isothermal (2)
variable tdamp equal 100*${timestep}                 # time constant for thermostat
variable seed equal 123457                # seed for thermostat

# generate the box and atom positions using a diamond lattice
variable a equal 3.1652

boundary	p p p

lattice         bcc $a
region		box prism 0 3.0 0 3.0 0 3.0 0.0 0.0 0.0
create_box	1 box
create_atoms	1 box
mass 1 ${mass1}
velocity	all create ${temp} 87287


