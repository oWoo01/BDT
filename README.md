# Brittle-to-Ductile Transition (in progress)


## Structure

- `in.s`  
  Scripts for computing surface energy of materials.

- `in.crack1`  
  Simulation inputs for crack tip K-test using **screening** method based on isotropic elastic theory.

- `in.crack2`  
  Simulation inputs for crack tip K-test using **blunting** method based on isotropic elastic theory.

- `load_idx_K_T`  
  Scripts and data for loading and analyzing K values in different crack systems at finite temperature.

## Goal

This project aims to provide reliable simulation tools to:

- Calculate surface energies accurately.
- Simulate crack tip behavior under various theoretical models (screening, blunting).
- Analyze the temperature-dependent loading of stress intensity factors (K) in crack systems.
- Facilitate better understanding of fracture mechanics at the atomic scale through LAMMPS simulations.

## Notes

- All simulations are implemented using **LAMMPS**.
- Post-processing and analysis are done with **Python** scripts.
- Data formats include `.in` for LAMMPS input, `.dump` and `.log` files for outputs.
- Theoretical background follows isotropic elasticity fracture mechanics principles.

## Contact

For questions, feedback, or contributions, please reach out to:

- GitHub: [jyzhang](https://github.com/oWoo01)  
- Email: jyzhang@example.com
