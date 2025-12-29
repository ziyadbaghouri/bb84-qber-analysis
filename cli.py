import argparse
from pathlib import Path
import numpy as np

from src.run_sweep import SweepConfig, run_sweep_parallel, save_sweep_csv
from src.visualize import (
    load_csv,
    plot_qber_heatmap,
    plot_qber_vs_qeve_for_fixed_p,
    plot_qber_vs_pnoise_for_fixed_q,
)

def main() -> None:
    parser = argparse.ArgumentParser(description="BB84 QBER simulation: sweep + plots")
    parser.add_argument("--n", type=int, default=50_000, help="Number of rounds per run")
    parser.add_argument("--seed", type=int, default=1, help="RNG seed")
    parser.add_argument("--noise-model", choices=["bitflip", "depolarizing"], default="depolarizing")

    parser.add_argument("--p-max", type=float, default=0.20)
    parser.add_argument("--p-steps", type=int, default=21)
    parser.add_argument("--q-steps", type=int, default=21)

    parser.add_argument("--p-curve", type=float, default=0.02, help="p_noise value for QBER vs q_eve plot")
    parser.add_argument("--q-curve", type=float, default=0.25, help="q_eve value for QBER vs p_noise plot")

    args = parser.parse_args()

    p_grid = tuple(np.linspace(0.0, args.p_max, args.p_steps))
    q_grid = tuple(np.linspace(0.0, 1.0, args.q_steps))

    cfg = SweepConfig(
        n=args.n,
        seed=args.seed,
        p_noise_values=p_grid,
        q_eve_values=q_grid,
    )

    results_dir = Path("results")
    csv_path = results_dir / f"sweep_n{cfg.n}_seed{cfg.seed}.csv"

    # 1) run sweep -> CSV
    df = run_sweep_parallel(cfg)
    save_sweep_csv(df, csv_path)
    print(f"[OK] Saved sweep CSV: {csv_path}")

    # 2) plots
    plots_dir = results_dir / "plots" / f"n{cfg.n}_seed{cfg.seed}"
    plot_qber_heatmap(df, plots_dir / "qber_heatmap.png")
    plot_qber_vs_qeve_for_fixed_p(df, args.p_curve, plots_dir / f"qber_vs_qeve_p{args.p_curve}.png")
    plot_qber_vs_pnoise_for_fixed_q(df, args.q_curve, plots_dir / f"qber_vs_pnoise_q{args.q_curve}.png")

    print(f"[OK] Saved plots to: {plots_dir}")

if __name__ == "__main__":
    main()
