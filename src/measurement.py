import numpy as np
from qutip import Qobj

from src.states import BB84States

def measure_in_basis(rho: Qobj, basis_id: int, rng: np.random.Generator) -> int:
    """
    Perform a projective measurement of a quantum state `rho`
    in the BB84 basis specified by `basis_id`.
    """
    # P0 projects onto bit 0, P1 projects onto bit 1
    P0, P1 = BB84States.proj[basis_id]

    # Born rule: probability of measuring bit 0
    p0 = (P0 * rho).tr().real

    # Numerical safety: clip due to floating-point errors
    p0 = min(max(p0, 0.0), 1.0)

    # Sample measurement outcome according to probabilities
    return 0 if rng.random() < p0 else 1
