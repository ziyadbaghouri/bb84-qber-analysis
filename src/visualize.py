"""
Visualization of BB84 Monte Carlo Results

This script produces:
1) A continuous QBER phase diagram (smooth / faded colors)
2) A binary security decision plot (SECURE vs ABORT)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# LOAD RESULTS
# =========================

RESULTS_PATH = Path("results/bb84_qber_sweep.csv")

if not RESULTS_PATH.exists():
    raise FileNotFoundError(f"Results file not found: {RESULTS_PATH}")

df = pd.read_csv(RESULTS_PATH)

QBER_THRESHOLD = df["qber_threshold"].iloc[0]


# =========================
# THEORETICAL BOUNDARY
# =========================

def theoretical_boundary(p_vals: np.ndarray) -> np.ndarray:
    """
    Exact security boundary from QBER = p/2 + (q/4)(1-p) = Q*:
        q_eve = 4(Q* - p/2) / (1 - p)

    Returns NaN where p >= 1 (undefined).
    """
    with np.errstate(invalid="ignore", divide="ignore"):
        q = 4.0 * (QBER_THRESHOLD - p_vals / 2.0) / (1.0 - p_vals)
    return np.where(p_vals < 1.0, q, np.nan)


# =========================
# FIGURE 1: CONTINUOUS QBER
# =========================

def plot_qber_continuous(df: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 5))

    sc = plt.scatter(
        df["p_noise"],
        df["q_eve"],
        c=df["qber"],
        cmap="viridis",
        s=80,
        edgecolors="k"
    )

    # Theoretical boundary
    p_vals = np.linspace(df["p_noise"].min(), df["p_noise"].max(), 300)
    q_bound = theoretical_boundary(p_vals)
    mask = q_bound >= 0

    plt.plot(
        p_vals[mask],
        q_bound[mask],
        "r--",
        linewidth=2,
        label="Theoretical threshold"
    )

    plt.xlabel("Channel noise probability $p_{noise}$")
    plt.ylabel("Eavesdropping probability $q_{eve}$")
    plt.title("Observed QBER (Monte Carlo Simulation)")
    plt.grid(True)

    cbar = plt.colorbar(sc)
    cbar.set_label("Observed QBER")

    plt.legend()
    plt.tight_layout()
    plt.show()


# =========================
# FIGURE 2: BINARY DECISION
# =========================

def plot_security_binary(df: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 5))

    secure_num = df["secure"].astype(int)

    sc = plt.scatter(
        df["p_noise"],
        df["q_eve"],
        c=secure_num,
        cmap="coolwarm",
        s=80,
        edgecolors="k"
    )

    # Theoretical boundary
    p_vals = np.linspace(df["p_noise"].min(), df["p_noise"].max(), 300)
    q_bound = theoretical_boundary(p_vals)
    mask = q_bound >= 0

    plt.plot(
        p_vals[mask],
        q_bound[mask],
        "k--",
        linewidth=2,
        label="Theoretical threshold"
    )

    plt.xlabel("Channel noise probability $p_{noise}$")
    plt.ylabel("Eavesdropping probability $q_{eve}$")
    plt.title("BB84 Security Regions (Secure vs Abort)")
    plt.grid(True)

    cbar = plt.colorbar(sc)
    cbar.set_label("Secure (1) / Abort (0)")

    plt.legend()
    plt.tight_layout()
    plt.show()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("Loaded BB84 sweep results")
    print(f"Points: {len(df)}")
    print(f"QBER threshold: {QBER_THRESHOLD:.4f} ({QBER_THRESHOLD*100:.2f}%)")

    # Main result: smooth QBER behavior
    plot_qber_continuous(df)

    # Decision view (useful for explanation)
    plot_security_binary(df)
