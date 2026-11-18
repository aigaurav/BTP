"""Step A: boundary-layer profiles far from vs near the junction (fine mesh, z = 0).

Reads Fluent XY files (velocity magnitude vs position) from data/stage3/,
computes delta99, displacement and momentum thickness, compares with the 1/7 law,
and writes figures/stepA_profiles.png.
Run: python3 stepA_profiles.py
"""
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WALL = 0.01           # floor top surface (y) and plate surface (x), m
FAR, NEAR = "#2a78d6", "#eb6834"   # validated categorical slots 1-2
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def read_xy(path):
    """Return {label: (pos, u)} sorted by position, duplicates removed."""
    text = open(path).read()
    out = {}
    for label, body in re.findall(r'\(\(xy/key/label "([^"]+)"\)(.*?)\n\)', text, re.S):
        pts = np.array([[float(a), float(b)] for a, b in
                        (ln.split() for ln in body.strip().splitlines() if ln.strip())])
        u, pos = pts[:, 0], pts[:, 1]
        pos, idx = np.unique(pos, return_index=True)
        out[label] = (pos, u[idx])
    return out


def bl_params(d, u, ue):
    """delta99 (interpolated), displacement and momentum thickness up to delta99 edge."""
    i = np.argmax(u >= 0.99 * ue)
    d99 = np.interp(0.99 * ue, [u[i - 1], u[i]], [d[i - 1], d[i]])
    m = d <= d.max()
    r = np.clip(u[m] / ue, 0, 1)
    dstar = np.trapezoid(1 - r, d[m])
    theta = np.trapezoid(r * (1 - r), d[m])
    return d99, dstar, theta


floor = read_xy("data/stage3/fine_BL_floor.xy")
plate = read_xy("data/stage3/fine_BL_plate.xy")
bis = read_xy("data/stage3/fine_BL_bisector.xy")["bisector"]

profiles = {
    "floor_far": floor["floor_far"], "floor_near": floor["floor_near"],
    "plate_far": plate["plate_far"], "plate_near": plate["plate_near"],
}

print(f"{'line':11s} {'Ue/max':>7s} {'d99 mm':>7s} {'d* mm':>6s} {'th mm':>6s} {'H':>5s}")
res = {}
for name, (pos, u) in profiles.items():
    d = pos - WALL
    if name.endswith("far"):
        ue = u[d > 0.035].mean()          # plateau = local edge velocity
        d99, ds, th = bl_params(d, u, ue)
        res[name] = (ue, d99)
        print(f"{name:11s} {ue:7.2f} {d99*1e3:7.1f} {ds*1e3:6.2f} {th*1e3:6.2f} {ds/th:5.2f}")
    else:
        print(f"{name:11s} {u.max():7.2f}  max at d = {d[np.argmax(u)]*1e3:.1f} mm; "
              f"u at d = 50 mm: {np.interp(0.05, d, u):.2f}")

# velocity at 10 mm from the wall: far vs near (junction effect)
for a, b in (("floor_far", "plate_near"), ("plate_far", "floor_near")):
    pa, ua = profiles[a]; pb, ub = profiles[b]
    print(f"u at 10 mm from wall: {a} {np.interp(0.01, pa - WALL, ua):.2f}  "
          f"{b} {np.interp(0.01, pb - WALL, ub):.2f} m/s")

# bisector: position = x + y ; distance from corner along diagonal
pos, u = bis
s = (pos - 0.02) / np.sqrt(2)
ue_b = u[s > 0.045].mean()
s99 = np.interp(0.99 * ue_b, u[np.argsort(s)], np.sort(s))
print(f"bisector: Ue {ue_b:.2f}, 99% reached at s = {s99*1e3:.1f} mm from corner "
      f"(sqrt2*delta99 floor/plate = {np.sqrt(2)*res['floor_far'][1]*1e3:.1f} / "
      f"{np.sqrt(2)*res['plate_far'][1]*1e3:.1f} mm)")

# ---------------- figure ----------------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), dpi=200, sharey=False)


def style(ax, title, xlabel):
    ax.set_title(title, loc="left", color=INK, fontsize=11)
    ax.set_xlabel("Velocity magnitude u (m/s)")
    ax.set_ylabel(xlabel)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_xlim(0, 40)


# (a) floor: far = floor_far (y-normal, 240 mm from plate); near = floor_near (10 mm from plate)
for ax, far, near, title, ylab, far_lbl, near_lbl in (
        (axes[0], "floor_far", "floor_near", "(a) Floor boundary layer",
         "Height above floor (mm)", "240 mm from plate", "10 mm from plate"),
        (axes[1], "plate_far", "plate_near", "(b) Plate boundary layer",
         "Distance from plate (mm)", "240 mm above floor", "10 mm above floor")):
    style(ax, title, ylab)
    pf, uf = profiles[far]; pn, un = profiles[near]
    ue, d99 = res[far]
    dd = np.linspace(0, d99, 100)
    ax.plot(ue * (dd / d99) ** (1 / 7), dd * 1e3, ls="--", lw=1.2, color=MUTED,
            label="1/7 power law")
    ax.plot(uf, (pf - WALL) * 1e3, color=FAR, lw=2, label=f"Far: {far_lbl}")
    ax.plot(un, (pn - WALL) * 1e3, color=NEAR, lw=2, label=f"Near: {near_lbl}")
    ax.axhline(d99 * 1e3, color=FAR, lw=0.8, ls=":")
    ax.text(1, d99 * 1e3 + 0.8, f"δ99 (far) = {d99*1e3:.1f} mm", color=INK, fontsize=9)
    ax.set_ylim(0, 50)
    ax.legend(frameon=False, loc="upper left", fontsize=9, bbox_to_anchor=(0, 0.93))

style(axes[2], "(c) Corner bisector (45° diagonal)", "Distance from corner along diagonal (mm)")
order = np.argsort(s)
axes[2].plot(u[order], s[order] * 1e3, color=FAR, lw=2)
axes[2].axhline(s99 * 1e3, color=FAR, lw=0.8, ls=":")
axes[2].text(1, s99 * 1e3 + 1, f"99 % of edge velocity at {s99*1e3:.0f} mm", color=INK, fontsize=9)
axes[2].set_ylim(0, 60)

fig.suptitle("Step A: boundary layers far from vs near the wall–plate junction "
             "(fine mesh, mid-length z = 0, U∞ = 36 m/s)", x=0.01, ha="left", fontsize=12, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig("figures/stepA_profiles.png", facecolor="#fcfcfb")
print("saved figures/stepA_profiles.png")
