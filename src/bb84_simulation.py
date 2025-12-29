from dataclasses import dataclass
from typing import Literal, Optional
import numpy as np

from src.states import prepare_density_matrix
from src.measurement import measure_in_basis
from src.eve import intercept_resend
from src.noise_models import apply_depolarizing_channel
from src.qber_analysis import sift_keys, qber as qber_fn



# Respesent BB84 simulation parameters 
@dataclass(frozen=True)
class BB84Params:
    n: int = 50_000
    p_noise: float = 0.0
    q_eve: float = 0.0
    seed: Optional[int] = 0


# Repreent BB84 simulation results
@dataclass
class BB84Result:
    qber: float
    n_total: int
    n_sifted: int
    n_errors: int
    params: BB84Params


def run_bb84(params: BB84Params) -> BB84Result:
    # validate inputs
    if params.n <= 0:
        raise ValueError("n must be positive")
    if not (0.0 <= params.p_noise <= 1.0):
        raise ValueError("p_noise must be in [0,1]")
    if not (0.0 <= params.q_eve <= 1.0):
        raise ValueError("q_eve must be in [0,1]")

    rng = np.random.default_rng(params.seed)
    N = params.n

    # Alice + Bob choices
    alice_bits  = rng.integers(0, 2, size=N, dtype=np.int8)
    alice_bases = rng.integers(0, 2, size=N, dtype=np.int8)
    bob_bases   = rng.integers(0, 2, size=N, dtype=np.int8)

    # No bits for Bob yet
    bob_bits = np.empty(N, dtype=np.int8)

    # run each BB84 round
    for i in range(N):
        # Alice prepares rho
        rho = prepare_density_matrix(int(alice_bases[i]), int(alice_bits[i]))

        # Eve intercepts with probability q_eve
        if rng.random() < params.q_eve:
            rho = intercept_resend(rho, rng)

        # Channel noise
        rho = apply_depolarizing_channel(rho, params.p_noise)

        # Bob measures in his chosen basis
        bob_bits[i] = measure_in_basis(rho, int(bob_bases[i]), rng)

    # sifting + QBER
    a_sift, b_sift = sift_keys(alice_bits, bob_bits, alice_bases, bob_bases)
    q = qber_fn(a_sift, b_sift)
    n_err = int(np.sum(a_sift != b_sift)) if a_sift.size else 0

    return BB84Result(
        qber=q,
        n_total=N,
        n_sifted=int(a_sift.size),
        n_errors=n_err,
        params=params
    )
