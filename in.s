units       metal
boundary    p p p
atom_style  atomic

read_data   Mo_${ori}.lmp

pair_style  eam/alloy
pair_coeff  * * ../../BDT/p_func/mo.fs.eam.alloy Mo

minimize    1e-15 1e-15 100000 100000

fix         1 all box/relax iso 0.0
minimize    1e-15 1e-15 100000 100000

unfix       1
minimize    1e-15 1e-15 100000 100000

fix         1 all box/relax iso 0.0
minimize    1e-15 1e-15 100000 100000

unfix       1
minimize    1e-15 1e-15 100000 100000

variable    E00 equal pe
variable    E0 equal ${E00}

change_box  all z delta -30 30 units box
write_data  delta.data
minimize    1e-15 1e-15 100000 100000

variable    E11 equal pe
variable    E1 equal ${E11}

variable    gamma equal (${E1}-${E0})/2/(xhi-xlo)/(yhi-ylo)

print       "z orientation: ${ori}" append gammas.txt screen no
print       "E0 = ${E0}" append gammas.txt screen no
print       "E1 = ${E1}" append gammas.txt screen no
print       "surface energy = ${gamma} eV/Å2" append gammas.txt screen no

