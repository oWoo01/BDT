units       metal
boundary    p p p
atom_style  atomic

read_data   W_${ori}.lmp

pair_style  eam/fs
pair_coeff  * * w_eam3.fs W

minimize    1e-15 1e-15 100000 100000

fix         1 all box/relax iso 0.0
minimize    1e-15 1e-15 100000 100000

unfix       1
minimize    1e-15 1e-15 100000 100000

fix         1 all box/relax iso 0.0
minimize    1e-15 1e-15 100000 100000

unfix       1
minimize    1e-15 1e-15 100000 100000

velocity    all create $T 83721
fix         ens all nvt temp $T $T $(100*dt) 
run         100000

variable    E00 equal pe
variable    E0 equal ${E00}

change_box  all z delta -30 30 units box
write_data  delta.data
minimize    1e-15 1e-15 100000 100000
run         100000

variable    E11 equal pe
variable    E1 equal ${E11}

variable    gamma equal (${E1}-${E0})/2/(xhi-xlo)/(yhi-ylo)

print       "${ori} $T ${E0} ${E1} ${gamma}" append gammasT.txt screen no

