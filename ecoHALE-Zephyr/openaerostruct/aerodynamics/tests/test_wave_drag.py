import unittest
import numpy as np
from openaerostruct.aerodynamics.wave_drag import WaveDrag
from openaerostruct.utils.testing import run_test, get_default_surfaces
from openmdao.api import Group, IndepVarComp, BsplinesComp
import numpy as np

class Test(unittest.TestCase):

    def test(self):
        surface = get_default_surfaces()[0]
        surface['with_wave'] = True
        surface['t_over_c_cp'] = np.array([0.15, 0.21, 0.03, 0.05])

        nx = surface['mesh'].shape[0]
        ny = surface['mesh'].shape[1]
        n_cp = len(surface['t_over_c_cp'])

        group = Group()

        indep_var_comp = IndepVarComp()
        indep_var_comp.add_output('t_over_c_cp', val=surface['t_over_c_cp'])
        indep_var_comp.add_output('Mach_number', val=.95)
        indep_var_comp.add_output('CL', val=0.7)
        indep_var_comp.add_output('widths', val = np.array([12.14757848, 11.91832712, 11.43730892]),units='m')
        indep_var_comp.add_output('cos_sweep', val = np.array([10.01555924,  9.80832351,  9.79003729]),units='m')
        indep_var_comp.add_output('chords', val = np.array([ 2.72835132,  5.12528179,  7.88916016, 13.6189974]),units='m')
        group.add_subsystem('indep_var_comp', indep_var_comp, promotes=['*'])

        group.add_subsystem('t_over_c_bsp', BsplinesComp(
            in_name='t_over_c_cp', out_name='t_over_c',
            num_control_points=n_cp, num_points=int(ny-1),
            bspline_order=min(n_cp, 4), distribution='uniform'),
            promotes_inputs=['t_over_c_cp'], promotes_outputs=['t_over_c'])

        comp = WaveDrag(surface=surface)
        group.add_subsystem('wavedrag', comp, promotes=['*'])

        run_test(self, group, complex_flag=True)

if __name__ == '__main__':
    unittest.main()
