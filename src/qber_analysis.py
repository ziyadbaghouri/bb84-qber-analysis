import numpy as np
from typing import Tuple

def sift_keys(
    alice_bits: np.ndarray,
    bob_bits: np.ndarray,
    alice_bases: np.ndarray,
    bob_bases: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    BB84 sifting step: keep only positions where Alice and Bob used the same basis.
    Returns (alice_sifted, bob_sifted).
    """
    keep_mask = (alice_bases == bob_bases)
    return alice_bits[keep_mask], bob_bits[keep_mask]


def qber(alice_sifted: np.ndarray, bob_sifted: np.ndarray) -> float:
    """
    Quantum Bit Error Rate over the sifted keys:
    QBER = (# mismatches) / (length of sifted key)
    """
    n = int(alice_sifted.size)
    if n == 0:
        return float("nan")

    return float(np.mean(alice_sifted != bob_sifted))


def count_errors(alice_sifted: np.ndarray, bob_sifted: np.ndarray) -> int:
    """
    Count the number of mismatched bits between Alice and Bob in the sifted key.
    """
    return int(np.sum(alice_sifted != bob_sifted))
