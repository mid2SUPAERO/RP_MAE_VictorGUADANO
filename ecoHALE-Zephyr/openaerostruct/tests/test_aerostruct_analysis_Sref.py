from __future__ import division, print_function
from openmdao.utils.assert_utils import assert_rel_error
import unittest
import numpy as np

from openaerostruct.geometry.utils import generate_mesh

from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint

from openmdao.api import IndepVarComp, Problem, Group, NewtonSolver, ScipyIterativeSolver, LinearBlockGS, NonlinearBlockGS, DirectSolver, LinearBlockGS, PetscKSP, ScipyOptimizeDriver
from openaerostruct.utils.constants import grav_constant


class Test(unittest.TestCase):

    def test(self):
        # Create a dictionary to store options about the surface
        mesh_dict = {'num_y' : 5,
                     'num_x' : 2,
                     'wing_type' : 'CRM',
                     'symmetry' : True,
                     'num_twist_cp' : 5}

        mesh, twist_cp = generate_mesh(mesh_dict)

        surf_dict = {
                    # Wing definition
                    'name' : 'wing',        # name of the surface
                    'symmetry' : True,     # if true, model one half of wing
                                            # reflected across the plane y = 0
                    'S_ref_type' : 'wetted', # how we compute the wing area,
                                             # can be 'wetted' or 'projected'
                    'fem_model_type' : 'tube',

                    'thickness_cp' : np.array([.1, .2, .3]),

                    'twist_cp' : twist_cp,
                    'mesh' : mesh,

                    # Aerodynamic performance of the lifting surface at
                    # an angle of attack of 0 (alpha=0).
                    # These CL0 and CD0 values are added to the CL and CD
                    # obtained from aerodynamic analysis of the surface to get
                    # the total CL and CD.
                    # These CL0 and CD0 values do not vary wrt alpha.
                    'CL0' : 0.0,            # CL of the surface at alpha=0
                    'CD0' : 0.015,            # CD of the surface at alpha=0

                    # Airfoil properties for viscous drag calculation
                    'k_lam' : 0.05,         # percentage of chord with laminar
                                            # flow, used for viscous drag
                    't_over_c_cp' : np.array([0.15]),      # thickness over chord ratio (NACA0015)
                    'c_max_t' : .303,       # chordwise location of maximum (NACA0015)
                                            # thickness
                    'with_viscous' : True,
                    'with_wave' : False,     # if true, compute wave drag

                    # Structural values are based on aluminum 7075
                    'E' : 70.e9,            # [Pa] Young's modulus of the spar
                    'G' : 30.e9,            # [Pa] shear modulus of the spar
                    'yield' : 500.e6 / 2.5, # [Pa] yield stress divided by 2.5 for limiting case
                    'mrho' : 3.e3,          # [kg/m^3] material density
                    'fem_origin' : 0.35,    # normalized chordwise location of the spar
                    'wing_weight_ratio' : 2.,
                    'struct_weight_relief' : False,    # True to add the weight of the structure to the loads on the structure
                    'distributed_fuel_weight' : False,
                    # Constraints
                    'exact_failure_constraint' : False, # if false, use KS function
                    }

        surfaces = [surf_dict]

        # Create the problem and assign the model group
        prob = Problem()

        # Add problem information as an independent variables component
        indep_var_comp = IndepVarComp()
        indep_var_comp.add_output('v', val=248.136, units='m/s')
        indep_var_comp.add_output('alpha', val=5., units='deg')
        indep_var_comp.add_output('Mach_number', val=0.84)
        indep_var_comp.add_output('re', val=1.e6, units='1/m')
        indep_var_comp.add_output('rho', val=0.38, units='kg/m**3')
        indep_var_comp.add_output('CT', val=grav_constant * 17.e-6, units='1/s')
        indep_var_comp.add_output('R', val=11.165e6, units='m')
        indep_var_comp.add_output('W0', val=0.4 * 3e5,  units='kg')
        indep_var_comp.add_output('speed_of_sound', val=295.4, units='m/s')
        indep_var_comp.add_output('load_factor', val=1.)
        indep_var_comp.add_output('empty_cg', val=np.zeros((3)), units='m')
        indep_var_comp.add_output('S_ref_total', val=150.0, units='m**2')

        prob.model.add_subsystem('prob_vars',
             indep_var_comp,
             promotes=['*'])

        # Loop over each surface in the surfaces list
        for surface in surfaces:

            # Get the surface name and create a group to contain components
            # only for this surface
            name = surface['name']

            aerostruct_group = AerostructGeometry(surface=surface)

            # Add tmp_group to the problem with the name of the surface.
            prob.model.add_subsystem(name, aerostruct_group)

        # Loop through and add a certain number of aero points
        for i in range(1):

            point_name = 'AS_point_{}'.format(i)
            # Connect the parameters within the model for each aero point

            # Create the aero point group and add it to the model
            AS_point = AerostructPoint(surfaces=surfaces,user_specified_Sref=True)

            prob.model.add_subsystem(point_name, AS_point)

            # Connect flow properties to the analysis point
            prob.model.connect('v', point_name + '.v')
            prob.model.connect('alpha', point_name + '.alpha')
            prob.model.connect('Mach_number', point_name + '.Mach_number')
            prob.model.connect('re', point_name + '.re')
            prob.model.connect('rho', point_name + '.rho')
            prob.model.connect('CT', point_name + '.CT')
            prob.model.connect('R', point_name + '.R')
            prob.model.connect('W0', point_name + '.W0')
            prob.model.connect('speed_of_sound', point_name + '.speed_of_sound')
            prob.model.connect('empty_cg', point_name + '.empty_cg')
            prob.model.connect('load_factor', point_name + '.load_factor')
            prob.model.connect('S_ref_total', point_name + '.S_ref_total')

            for surface in surfaces:

                com_name = point_name + '.' + name + '_perf'
                prob.model.connect(name + '.local_stiff_transformed', point_name + '.coupled.' + name + '.local_stiff_transformed')
                prob.model.connect(name + '.nodes', point_name + '.coupled.' + name + '.nodes')

                # Connect aerodyamic mesh to coupled group mesh
                prob.model.connect(name + '.mesh', point_name + '.coupled.' + name + '.mesh')

                # Connect performance calculation variables
                prob.model.connect(name + '.radius', com_name + '.radius')
                prob.model.connect(name + '.thickness', com_name + '.thickness')
                prob.model.connect(name + '.nodes', com_name + '.nodes')
                prob.model.connect(name + '.cg_location', point_name + '.' + 'total_perf.' + name + '_cg_location')
                prob.model.connect(name + '.structural_mass', point_name + '.' + 'total_perf.' + name + '_structural_mass')
                prob.model.connect(name + '.t_over_c', com_name + '.t_over_c')

        # Set up the problem
        prob.setup()

        # from openmdao.api import view_model
        # view_model(prob)

        prob.run_model()

        assert_rel_error(self, prob['AS_point_0.CL'][0], 1.5775046966345903, 1e-6)
        assert_rel_error(self, prob['AS_point_0.CM'][1], -1.61358383281, 1e-5)


if __name__ == '__main__':
    unittest.main()
