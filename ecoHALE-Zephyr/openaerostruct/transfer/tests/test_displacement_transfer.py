import unittest
from openmdao.api import IndepVarComp, Group

from openaerostruct.transfer.displacement_transfer import DisplacementTransfer
from openaerostruct.utils.testing import run_test, get_default_surfaces


class Test(unittest.TestCase):

    def test(self):
        surface = get_default_surfaces()[0]

        comp = DisplacementTransfer(surface=surface)

        group = Group()

        indep_var_comp = IndepVarComp()

        ny = surface['mesh'].shape[1]

        mesh = surface['mesh']

        indep_var_comp.add_output('mesh', val=mesh, units='m')

        group.add_subsystem('indep_var_comp', indep_var_comp, promotes=['*'])
        group.add_subsystem('load', comp, promotes=['*'])

        run_test(self, group, complex_flag=True)


if __name__ == '__main__':
    unittest.main()
