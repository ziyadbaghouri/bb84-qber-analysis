from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Convert long-form dataframe into grid arrays for plotting
def _pivot_qber(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    p_values = np.sort(df["p_noise"].unique())
    q_values = np.sort(df["q_eve"].unique())

    grid = df.pivot(index="q_eve", columns="p_noise", values="qber")
    Z = grid.to_numpy()  # rows correspond to q_values, cols to p_values
    return p_values, q_values, Z

# Heatmap of QBER over (p_noise, q_eve)
def plot_qber_heatmap(df: pd.DataFrame, out_path: Path) -> None:
    p_values, q_values, Z = _pivot_qber(df)
    fig, ax = plt.subplots()
    im = ax.imshow(
        Z,
        origin="lower",
        aspect="auto",
        extent=[p_values.min(), p_values.max(), q_values.min(), q_values.max()],
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("QBER")
    ax.set_xlabel("p_noise")
    ax.set_ylabel("q_eve")
    title = f"QBER heatmap"
    ax.set_title(title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

# Plot QBER vs q_eve for a chosen p_noise value
def plot_qber_vs_qeve_for_fixed_p(df: pd.DataFrame, p_noise: float, out_path: Path) -> None:
    # choose closest p_noise available
    p_vals = np.sort(df["p_noise"].unique())
    p_sel = float(p_vals[np.argmin(np.abs(p_vals - p_noise))])
    sub = df[df["p_noise"] == p_sel].sort_values("q_eve")
    x = sub["q_eve"].to_numpy()
    y = sub["qber"].to_numpy()
    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o")
    ax.set_xlabel("q_eve")
    ax.set_ylabel("QBER")
    ax.set_title(f"QBER vs q_eve at p_noise={p_sel}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

# Plot QBER vs p_noise for a chosen q_eve value
def plot_qber_vs_pnoise_for_fixed_q(df: pd.DataFrame, q_eve: float, out_path: Path) -> None:
    q_vals = np.sort(df["q_eve"].unique())
    q_sel = float(q_vals[np.argmin(np.abs(q_vals - q_eve))])
    sub = df[df["q_eve"] == q_sel].sort_values("p_noise")
    x = sub["p_noise"].to_numpy()
    y = sub["qber"].to_numpy()
    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o")
    ax.set_xlabel("p_noise")
    ax.set_ylabel("QBER")
    ax.set_title(f"QBER vs p_noise at q_eve={q_sel}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)