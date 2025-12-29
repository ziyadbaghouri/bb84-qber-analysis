from dataclasses import dataclass
from qutip import basis, ket2dm, qeye, Qobj

# Basis identifiers
RECTILINEAR = 0   # '+' basis
DIAGONAL    = 1   # 'x' basis


@dataclass(frozen=True)
class BB84States:
    """
    Collection of BB84 quantum states and measurement operators.

    Basis convention:
      - RECTILINEAR (0): |0>, |1>
      - DIAGONAL    (1): (|0> ± |1>) / sqrt(2)
    """

    # Computational basis states
    ket0 = basis(2, 0)
    ket1 = basis(2, 1)

    # Diagonal basis states
    ket_plus  = (ket0 + ket1).unit()
    ket_minus = (ket0 - ket1).unit()

    # Mapping: (basis_id, bit) -> ket
    state = {
        (RECTILINEAR, 0): ket0,
        (RECTILINEAR, 1): ket1,
        (DIAGONAL,    0): ket_plus,
        (DIAGONAL,    1): ket_minus,
    }

    # Projective measurement operators for each basis: [P(bit=0), P(bit=1)]
    proj = {
        RECTILINEAR: [ket0 * ket0.dag(), ket1 * ket1.dag()],
        DIAGONAL:    [ket_plus * ket_plus.dag(), ket_minus * ket_minus.dag()],
    }

    # 2x2 identity operator
    I2 = qeye(2)


def prepare_density_matrix(basis_id: int, bit: int) -> Qobj:
    """
    Prepare the density matrix corresponding to Alice's choice of
    basis and bit in the BB84 protocol.
    """
    psi = BB84States.state[(basis_id, bit)]
    return ket2dm(psi)
