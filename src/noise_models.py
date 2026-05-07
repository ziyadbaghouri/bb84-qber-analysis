import numpy as np
from qutip import Qobj

from src.states import BB84States

def apply_depolarizing_channel(rho: Qobj, p_noise: float, rng: np.random.Generator) -> Qobj:
    """
    Depolarizing channel (explicit version):

    - With probability (1 - p_noise): state is unchanged
    - With probability p_noise: state is replaced by I/2
    """
    if rng.random() < p_noise:
        # Photon is fully randomized
        return BB84States.I2 / 2
    else:
        # Photon is transmitted correctly
        return rho

