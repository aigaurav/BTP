"""Convergence histories of the monitors for the three meshes (grid study).

Input : data/convergence/{coarse,medium,fine}/{cd,v_corner,v_wake}-rfile.out
Output: figures/convergence_monitors.png, and printed means over the last 200 iterations.
Note  : on the fine mesh, iterations 1-177 were computed with default reference values
        (U = 1 m/s, A = 1 m^2). The flow was unaffected; cd is rescaled here by
        1 / (36^2 x 0.1472) = 1/190.77 so the whole history uses the correct reference.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
MESH = [("coarse", "Coarse (0.53 M)", "#2a78d6"),
        ("medium", "Medium (1.15 M)", "#eb6834"),
        ("fine", "Fine (2.53 M)", "#1baf7a")]          # validated slots 1-3 (all-pairs safe)
MON = [("cd", "C_d", "Drag coefficient C_d"),
       ("v_corner", "v_corner (m/s)", "Corner velocity, (0.02, 0.02, 0)"),
       ("v_wake", "v_wake (m/s)", "Corner-wake velocity, (0.02, 0.02, −0.35)")]
REF_FIX = 1 / (36.0**2 * 0.1472)
SWITCH = 178          # first fine-mesh iteration with correct reference values

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})

fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), dpi=200)
print(f"{'mesh':7s} {'monitor':9s} {'mean(last200)':>14s} {'half-range':>11s} {'rel %':>6s}")
for ax, (key, ylab, title) in zip(axes, MON):
    lo, hi = np.inf, -np.inf
    for mesh, label, col in MESH:
        d = np.loadtxt(f"data/convergence/{mesh}/{key}-rfile.out", skiprows=3)
        it, val = d[:, 0], d[:, 1].copy()
        if mesh == "fine" and key == "cd":
            val[it < SWITCH] *= REF_FIX
        ax.plot(it, val, color=col, lw=1.6, label=label)
        last = val[-200:]
        m, h = last.mean(), (last.max() - last.min()) / 2
        print(f"{mesh:7s} {key:9s} {m:14.6g} {h:11.3g} {100*h/m:6.2f}")
        tail = val[it > 60]
        lo, hi = min(lo, tail.min()), max(hi, tail.max())
        ax.annotate(f"{m:.4g}", xy=(it[-1], m), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8, color=INK)
    pad = 0.15 * (hi - lo)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_xlim(0, 560)
    ax.axvspan(300, 500, color=GRID, alpha=0.6, lw=0)
    ax.text(400, hi + 0.08 * (hi - lo), "averaging window", ha="center", fontsize=8, color=MUTED)
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    ax.set_xlabel("Iteration")
    ax.set_ylabel(ylab)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].legend(frameon=False, fontsize=9, loc="center left", bbox_to_anchor=(0.3, 0.56))
fig.suptitle("Monitor convergence on the three grids (steady RANS, SST k–ω, coupled pseudo-transient). "
             "Values on the right = mean of the last 200 iterations", x=0.01, ha="left",
             fontsize=11, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig("figures/convergence_monitors.png", facecolor=SURF)
print("saved figures/convergence_monitors.png")
