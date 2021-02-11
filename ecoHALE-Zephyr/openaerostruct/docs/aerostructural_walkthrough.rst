.. _Aerostructural_Walkthrough:

Aerostructural Walkthrough
==========================

With aerodynamic- and structural-only analyses done, we now examine an aerostructural design problem.
The construction of the problem follows the same logic as outlined in :ref:`Aerodynamic_Optimization_Walkthrough`, though with some added details.
For example, we use an `AerostructPoint` group instead of an `AeroGroup` because it contains the additional components needed for aerostructural optimization.
Additionally, we have more variable connections due to the more complex problem formulation.

  .. embed-code::
      openaerostruct.tests.test_aerostruct.Test.test
      :layout: interleave
