from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import os
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.bb84_simulation import BB84Params, run_bb84


# Either we enter the params through the cmd or with this cfg directly
@dataclass(frozen=True)
class SweepConfig:
    n: int = 50000
    seed: int = 1
    p_noise_values: tuple[float, ...] = tuple(np.linspace(0.0, 0.20, 21))
    q_eve_values: tuple[float, ...]   = tuple(np.linspace(0.0, 1.00, 21))


# run for a single (p_noise, q_eve) point
def _one_point(args: tuple[int, int, float, float]) -> dict:
    n, seed, p_noise, q_eve = args
    params = BB84Params(n=n,p_noise=float(p_noise), q_eve=float(q_eve), seed=int(seed))
    res = run_bb84(params)
    return {
        "n": res.n_total,
        "seed": res.params.seed,
        "p_noise": res.params.p_noise,
        "q_eve": res.params.q_eve,
        "qber": res.qber,
        "n_sifted": res.n_sifted,
        "n_errors": res.n_errors,
    }

def run_sweep_parallel(cfg: SweepConfig) -> pd.DataFrame:
    points = [(cfg.n, cfg.seed, p, q) for p in cfg.p_noise_values for q in cfg.q_eve_values]
    workers = os.cpu_count()
    rows: list[dict] = []
    total = len(points)

    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_one_point, pt) for pt in points]
        done = 0
        for fut in as_completed(futures):
            rows.append(fut.result())
            done += 1
            if (done % max(1, total // 20) == 0 or done == total):
                print(f"Progress: {done}/{total} ({done/total:.0%})")

    df = pd.DataFrame(rows)

    # sort for nicer CSV / plotting
    df = df.sort_values(["p_noise", "q_eve"]).reset_index(drop=True)
    return df

def save_sweep_csv(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
