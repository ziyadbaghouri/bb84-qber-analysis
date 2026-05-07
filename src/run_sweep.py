from dataclasses import dataclass
from pathlib import Path
import os
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from bb84_simulation import BB84Params, run_bb84, compute_qber_threshold


# =========================
# SWEEP CONFIGURATION
# =========================

@dataclass(frozen=True)
class SweepConfig:
    """
    Parameter sweep configuration
    """
    n: int = 50_000
    seed: int = 1
    p_noise_values: tuple[float, ...] = tuple(np.linspace(0.0, 0.20, 21))
    q_eve_values: tuple[float, ...]   = tuple(np.linspace(0.0, 1.00, 21))


# =========================
# GLOBAL: SECURITY THRESHOLD
# =========================

# Compute once (theoretical BB84 bound)
QBER_THRESHOLD = compute_qber_threshold()


# =========================
# SINGLE SWEEP POINT
# =========================

def _run_single_point(args: tuple[int, int, float, float]) -> dict:
    """
    Run BB84 simulation for a single (p_noise, q_eve) pair.
    Executed in a worker process.
    """
    n, seed, p_noise, q_eve = args

    params = BB84Params(
        n=n,
        p_noise=float(p_noise),
        q_eve=float(q_eve),
        seed=int(seed),
    )

    res = run_bb84(params)

    secure = res.qber <= QBER_THRESHOLD

    return {
        "n": res.n_total,
        "seed": seed,
        "p_noise": p_noise,
        "q_eve": q_eve,
        "qber": res.qber,
        "n_sifted": res.n_sifted,
        "n_errors": res.n_errors,
        "qber_threshold": QBER_THRESHOLD,
        "secure": secure,
        "decision": "SECURE" if secure else "ABORT",
    }


# =========================
# PARALLEL SWEEP
# =========================

def run_sweep_parallel(cfg: SweepConfig) -> pd.DataFrame:
    """
    Run the BB84 parameter sweep in parallel and return results as a DataFrame.
    """

    # Cartesian product of parameters
    points = [
        (cfg.n, cfg.seed, p, q)
        for p in cfg.p_noise_values
        for q in cfg.q_eve_values
    ]

    total = len(points)
    workers = os.cpu_count() or 1
    rows: list[dict] = []

    print(f"Running sweep with {total} points using {workers} workers")
    print(f"QBER security threshold: {QBER_THRESHOLD:.4f} ({QBER_THRESHOLD*100:.2f}%)")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_single_point, pt) for pt in points]

        completed = 0
        for future in as_completed(futures):
            rows.append(future.result())
            completed += 1

            # Progress update (every ~5%)
            if completed % max(1, total // 20) == 0 or completed == total:
                print(f"Progress: {completed}/{total} ({completed/total:.0%})")

    # Build DataFrame
    df = pd.DataFrame(rows)

    # Sort for clean plotting / CSV
    df = df.sort_values(["p_noise", "q_eve"]).reset_index(drop=True)

    return df


# =========================
# SAVE RESULTS
# =========================

def save_sweep_csv(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved sweep results to {out_path}")


# =========================
# MAIN (OPTIONAL)
# =========================

if __name__ == "__main__":

    cfg = SweepConfig(
        n=50_000,
        seed=1,
        p_noise_values=tuple(np.linspace(0.0, 0.15, 16)),
        q_eve_values=tuple(np.linspace(0.0, 1.0, 21)),
    )

    df = run_sweep_parallel(cfg)

    save_sweep_csv(
        df,
        Path("results/bb84_qber_sweep.csv")
    )
