import unittest
import numpy as np

from openmdao.api import Group, IndepVarComp
from openaerostruct.structures.weight import Weight
from openaerostruct.utils.testing import run_test, get_default_surfaces


np.random.seed(314)

class Test(unittest.TestCase):

    def test(self):
        surface = get_default_surfaces()[0]
        ny = surface['mesh'].shape[1]

        group = Group()

        ivc = IndepVarComp()
        ivc.add_output('nodes', val=np.random.random_sample((ny, 3)))

        comp = Weight(surface=surface)

        group.add_subsystem('ivc', ivc, promotes=['*'])
        group.add_subsystem('comp', comp, promotes=['*'])

        run_test(self, group, compact_print=False, complex_flag=True)


if __name__ == '__main__':
    unittest.main()
