"""
BB84 Monte Carlo Simulation with Theoretical QBER Threshold

This file:
1) Simulates the BB84 protocol with noise and intercept–resend eavesdropping
2) Computes the observed QBER from Monte Carlo trials
3) Computes the maximum tolerable QBER using the Shor–Preskill security bound
4) Compares simulation results to the proven security threshold
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

# =========================
# PARAMETERS & DATA MODELS
# =========================

@dataclass(frozen=True)
class BB84Params:
    """
    BB84 simulation parameters
    """
    n: int = 50_000              # number of photons
    p_noise: float = 0.0         # channel noise probability
    q_eve: float = 0.0           # Eve interception probability
    seed: Optional[int] = 0      # RNG seed


@dataclass
class BB84Result:
    """
    BB84 simulation results
    """
    qber: float
    n_total: int
    n_sifted: int
    n_errors: int
    params: BB84Params


# =========================
# INFORMATION-THEORETIC PART
# =========================

def binary_entropy(q):
    """
    Binary entropy function h2(q), vectorized.
    Works for scalars or NumPy arrays.
    """
    q = np.asarray(q)

    h = np.zeros_like(q, dtype=float)
    mask = (q > 0.0) & (q < 1.0)

    h[mask] = (
        -q[mask] * np.log2(q[mask])
        - (1 - q[mask]) * np.log2(1 - q[mask])
    )

    return h



def bb84_key_rate(qber: float) -> float:
    """
    Asymptotic BB84 secret key rate (Shor–Preskill bound):

        K(Q) = 1 - 2 h2(Q)

    Secure key extraction requires K(Q) > 0
    """
    return 1.0 - 2.0 * binary_entropy(qber)


def compute_qber_threshold() -> float:
    """
    Compute the maximum tolerable QBER by solving:

        1 - 2 h2(Q) = 0
    """
    q_vals = np.linspace(0.0, 0.5, 1_000_000)
    rates = bb84_key_rate(q_vals)
    idx = np.where(rates <= 0)[0][0]
    return q_vals[idx]


# =========================
# BB84 SIMULATION CORE
# =========================

def run_bb84(params: BB84Params) -> BB84Result:
    """
    Monte Carlo simulation of BB84
    """

    # ---- Input validation ----
    if params.n <= 0:
        raise ValueError("n must be positive")
    if not (0.0 <= params.p_noise <= 1.0):
        raise ValueError("p_noise must be in [0,1]")
    if not (0.0 <= params.q_eve <= 1.0):
        raise ValueError("q_eve must be in [0,1]")

    rng = np.random.default_rng(params.seed)
    N = params.n

    # ---- Random choices ----
    alice_bits  = rng.integers(0, 2, size=N)
    alice_bases = rng.integers(0, 2, size=N)
    bob_bases   = rng.integers(0, 2, size=N)

    bob_bits = np.empty(N, dtype=int)

    # ---- Main BB84 loop ----
    for i in range(N):

        # Alice prepares a bit
        a_bit = alice_bits[i]
        a_basis = alice_bases[i]

        # Bob measures
        if rng.random() < params.q_eve:
            # Eve intercept–resend
            eve_basis = rng.integers(0, 2)
            eve_bit = a_bit if eve_basis == a_basis else rng.integers(0, 2)
            sent_bit = eve_bit
        else:
            sent_bit = a_bit

        # Channel noise
        if rng.random() < params.p_noise:
            sent_bit = rng.integers(0, 2)

        # Bob measurement
        if bob_bases[i] == a_basis:
            bob_bits[i] = sent_bit
        else:
            bob_bits[i] = rng.integers(0, 2)

    # ---- Basis reconciliation (sifting) ----
    keep = alice_bases == bob_bases
    a_sift = alice_bits[keep]
    b_sift = bob_bits[keep]

    # ---- QBER computation ----
    if a_sift.size == 0:
        qber = 0.0
        n_err = 0
    else:
        n_err = np.sum(a_sift != b_sift)
        qber = n_err / a_sift.size

    return BB84Result(
        qber=qber,
        n_total=N,
        n_sifted=int(a_sift.size),
        n_errors=int(n_err),
        params=params
    )


# =========================
# MAIN ENTRY POINT
# =========================

if __name__ == "__main__":

    # --- Simulation parameters ---
    params = BB84Params(
        n=50_000,
        p_noise=0.02,
        q_eve=0.20,
        seed=42
    )

    # --- Run simulation ---
    result = run_bb84(params)

    # --- Compute theoretical threshold ---
    qber_threshold = compute_qber_threshold()

    # --- Display results ---
    print("=== BB84 Monte Carlo Simulation ===")
    print(f"Total photons:     {result.n_total}")
    print(f"Sifted key size:   {result.n_sifted}")
    print(f"Errors observed:   {result.n_errors}")
    print(f"Observed QBER:     {result.qber:.4f} ({result.qber*100:.2f}%)")
    print()
    print("=== Security Threshold (Shor–Preskill) ===")
    print(f"Maximum QBER:      {qber_threshold:.4f} ({qber_threshold*100:.2f}%)")
    print()

    if result.qber <= qber_threshold:
        print("✔ Secure regime: secret key extraction is possible.")
    else:
        print("✘ Insecure regime: protocol must abort.")
