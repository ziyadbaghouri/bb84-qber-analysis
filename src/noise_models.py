from qutip import Qobj

from src.states import BB84States

def apply_depolarizing_channel(rho: Qobj, p_noise: float) -> Qobj:
    """
    Depolarizing channel:
    With probability (1 - p_noise), the quantum state is unchanged.
    With probability p_noise, the state is replaced by the maximally mixed state I/2.

    This models physical channel noise where the photon polarization is randomized.
    """
    return (1 - p_noise) * rho + p_noise * (BB84States.I2 / 2)
