import numpy as np
from qutip import Qobj

from src.measurement import measure_in_basis
from src.states import prepare_density_matrix


def intercept_resend(rho_in: Qobj, rng: np.random.Generator) -> Qobj:
    """
    Eve performs an intercept–resend attack.

    Steps:
    1) Eve randomly chooses a measurement basis (0: rectilinear, 1: diagonal)
    2) She measures the incoming quantum state in that basis
       → this collapses the state
    3) She re-prepares a new photon consistent with her measurement
    4) The new state is sent to Bob
    """
    eve_basis = int(rng.integers(0, 2))
    eve_bit = measure_in_basis(rho_in, eve_basis, rng)
    rho_out = prepare_density_matrix(eve_basis, eve_bit)
    return rho_out
