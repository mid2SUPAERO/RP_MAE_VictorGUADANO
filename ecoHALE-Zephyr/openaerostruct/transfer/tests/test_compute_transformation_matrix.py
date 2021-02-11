import unittest
import numpy as np
from openmdao.api import IndepVarComp, Group

from openaerostruct.transfer.compute_transformation_matrix import ComputeTransformationMatrix
from openaerostruct.utils.testing import run_test, get_default_surfaces


np.random.seed(314)

class Test(unittest.TestCase):

    def test(self):
        surface = get_default_surfaces()[0]

        comp = ComputeTransformationMatrix(surface=surface)

        group = Group()

        indep_var_comp = IndepVarComp()

        ny = surface['mesh'].shape[1]
        disp = np.random.random_sample((ny, 6)) * 100.

        indep_var_comp.add_output('disp', val=disp, units='m')

        group.add_subsystem('indep_var_comp', indep_var_comp, promotes=['*'])
        group.add_subsystem('trans_mtx', comp, promotes=['*'])

        run_test(self, group, complex_flag=True, method='cs')


if __name__ == '__main__':
    unittest.main()
