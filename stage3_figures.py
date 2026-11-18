"""Stage 3 report figures from Fluent ASCII exports (fine mesh).

Input : data/stage3/fine_planes_wall.zip  (fine_planes.csv: planes z = +0.2, +0.1, 0, -0.2;
                                           fine_wall.csv  : nodes on the L walls)
Output: figures/stepB_wz_planes.png, figures/stepB_wx_wy_z0.png,
        figures/stepD_isovels_vectors.png, figures/stepE_cf.png
        and printed numbers (circulation of the corner vortex, Cf near vs far).
Geometry: inside corner of the L at x = 0.01, y = 0.01 m; floor top y = 0.01; plate face x = 0.01;
flow in -z, leading edge z = +0.23, trailing edge z = -0.23. U_inf = 36 m/s.
"""
import io
import zipfile
import numpy as np
import pandas as pd
import os
import matplotlib
if os.environ.get("NO_TITLE"):
    import matplotlib.figure
    matplotlib.figure.Figure.suptitle = lambda self, *a, **k: None  # report version: caption replaces title
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from scipy.interpolate import griddata

ZIP = "data/stage3/fine_planes_wall.zip"
INK, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
WALL_C = "#9a9893"
# diverging blue <-> red, neutral gray midpoint (reference palette)
DIV = LinearSegmentedColormap.from_list(
    "div", ["#104281", "#2a78d6", "#9ec5f4", "#f0efec", "#f4b7a6", "#e34948", "#8f1d1d"])
SEQ = LinearSegmentedColormap.from_list(
    "seq", ["#f0efec", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
C0, C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"   # validated slots 1,2,3,7

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})


def load(name):
    with zipfile.ZipFile(ZIP) as z:
        df = pd.read_csv(io.BytesIO(z.read(name)), skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    return df


planes = load("fine_planes.csv")
wall = load("fine_wall.csv")
planes["zr"] = planes["z-coordinate"].round(3)
STATIONS = [(0.2, "z = +0.20 m"), (0.1, "z = +0.10 m"), (0.0, "z = 0"), (-0.2, "z = −0.20 m")]

# corner window (fluid only): 0.01..0.07 m in x and y -> plotted as mm from the walls
LO, HI, NG = 0.01, 0.07, 241
gx = np.linspace(LO, HI, NG)
GX, GY = np.meshgrid(gx, gx)


def field(z, col):
    d = planes[(planes["zr"] == z) & planes["x-coordinate"].between(LO - 0.004, HI + 0.004)
               & planes["y-coordinate"].between(LO - 0.004, HI + 0.004)]
    d = d[(d["x-coordinate"] >= LO - 1e-9) & (d["y-coordinate"] >= LO - 1e-9)]
    return griddata((d["x-coordinate"], d["y-coordinate"]), d[col], (GX, GY), method="linear")


def mm(a):
    return (a - LO) * 1e3


def decorate(ax, title):
    ax.set_title(title, loc="left", fontsize=7, color=INK, pad=10)
    ax.set_aspect("equal")
    ax.set_xlim(-3, 60); ax.set_ylim(-3, 60)
    ax.add_patch(plt.Rectangle((-3, -3), 3, 63, color=WALL_C, lw=0))    # plate
    ax.add_patch(plt.Rectangle((-3, -3), 63, 3, color=WALL_C, lw=0))    # floor
    ax.set_xlabel("Distance from plate (mm)", labelpad=1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ---------- numbers: corner vortex circulation per station ----------
dA = ((HI - LO) / (NG - 1)) ** 2
away = (GX - LO > 0.002) & (GY - LO > 0.002)      # exclude the thin near-wall skew layer
print("station   Gamma+ (m2/s)  Gamma- (m2/s)  max|wz| (1/s)  max in-plane |v| (m/s)")
circ = {}
for z, _ in STATIONS:
    wz = field(z, "z-vorticity")
    vx, vy = field(z, "x-velocity"), field(z, "y-velocity")
    m = away & np.isfinite(wz)
    gp = np.nansum(np.where(m & (wz > 0), wz, 0)) * dA
    gm = np.nansum(np.where(m & (wz < 0), wz, 0)) * dA
    circ[z] = (gp, gm)
    print(f"{z:+.2f}    {gp:12.4f}  {gm:12.4f}  {np.nanmax(np.abs(wz[m])):12.0f}  "
          f"{np.nanmax(np.hypot(vx, vy)[m]):10.2f}")

# ---------- Fig B1: wz at 4 stations ----------
fig, axes = plt.subplots(1, 4, figsize=(8.2, 2.75), dpi=200)
norm = TwoSlopeNorm(vcenter=0, vmin=-300, vmax=300)
for ax, (z, lab) in zip(axes, STATIONS):
    wz = field(z, "z-vorticity")
    cf = ax.contourf(mm(GX), mm(GY), np.clip(wz, -300, 300), levels=np.linspace(-300, 300, 25),
                     cmap=DIV, norm=norm, extend="both")
    gp, gm = circ[z]
    decorate(ax, lab)
    ax.text(58, 57, f"Γ+ = {gp*1e3:.1f}\nΓ− = {gm*1e3:.1f}  ×10⁻³ m²/s", ha="right", va="top",
            fontsize=5.5, color=INK, bbox=dict(fc=SURF, ec="none", alpha=0.85))
axes[0].set_ylabel("Height above floor (mm)")
cb = fig.colorbar(cf, ax=axes, shrink=0.85, pad=0.01, ticks=[-300, -150, 0, 150, 300])
cb.set_label("Streamwise vorticity ω_z (1/s)")
fig.suptitle("Step B: streamwise vorticity in the inside corner along the junction "
             "(fine mesh, viewed looking downstream; grey = plate and floor)",
             x=0.01, ha="left", fontsize=12, color=INK)
fig.savefig("figures/stepB_wz_planes.png", facecolor=SURF, bbox_inches="tight")
plt.close(fig)

# ---------- Fig B2: wx and wy at z = 0 ----------
fig, axes = plt.subplots(1, 2, figsize=(5.6, 2.7), dpi=200)
norm = TwoSlopeNorm(vcenter=0, vmin=-3000, vmax=3000)
for ax, col, lab in ((axes[0], "x-vorticity", "ω_x (floor boundary-layer vorticity)"),
                     (axes[1], "y-vorticity", "ω_y (plate boundary-layer vorticity)")):
    f = field(0.0, col)
    cf = ax.contourf(mm(GX), mm(GY), np.clip(f, -3000, 3000), levels=np.linspace(-3000, 3000, 25),
                     cmap=DIV, norm=norm, extend="both")
    decorate(ax, lab)
axes[0].set_ylabel("Height above floor (mm)")
cb = fig.colorbar(cf, ax=axes, shrink=0.85, pad=0.02)
cb.set_label("Vorticity (1/s)")
fig.suptitle("Step B: wall vorticity at mid-length (z = 0): floor and plate vortex lines meet in the corner",
             x=0.01, ha="left", fontsize=12, color=INK)
fig.savefig("figures/stepB_wx_wy_z0.png", facecolor=SURF, bbox_inches="tight")
plt.close(fig)

# ---------- Fig D: isovels + in-plane vectors ----------
fig, axes = plt.subplots(1, 4, figsize=(8.2, 2.75), dpi=200)
sub = slice(6, None, 12)                       # evenly spaced arrows every 3 mm
for ax, (z, lab) in zip(axes, STATIONS):
    U = field(z, "velocity-magnitude")
    vx, vy = field(z, "x-velocity"), field(z, "y-velocity")
    cf = ax.contourf(mm(GX), mm(GY), U, levels=np.linspace(0, 38, 20), cmap=SEQ, extend="max")
    cs = ax.contour(mm(GX), mm(GY), U, levels=[20, 25, 30, 33, 35, 36.5], colors=INK,
                    linewidths=0.45)
    ax.clabel(cs, fontsize=5, fmt="%g")
    ref = 2.0 if z > 0.15 else 0.3          # z = +0.2 cross-flow is ~10x stronger
    q = ax.quiver(mm(GX[sub, sub]), mm(GY[sub, sub]), vx[sub, sub], vy[sub, sub],
                  color=C1, scale=ref * 12, scale_units="width", width=0.006, headwidth=3.5)
    decorate(ax, lab)
    ax.quiverkey(q, 0.62, 1.02, ref, f"{ref:g} m/s", labelpos="E", coordinates="axes",
                 color=C1, fontproperties={"size": 6})
axes[0].set_ylabel("Height above floor (mm)")
cb = fig.colorbar(cf, ax=axes, shrink=0.85, pad=0.01)
cb.set_label("Velocity magnitude (m/s)")
fig.suptitle("Step D: isovels (black lines, m/s) and cross-flow vectors (orange; reference arrow above each panel) "
             "in the inside corner", x=0.01, ha="left", fontsize=12, color=INK)
fig.savefig("figures/stepD_isovels_vectors.png", facecolor=SURF, bbox_inches="tight")
plt.close(fig)

# ---------- Fig E: skin friction near vs far from the corner ----------
fl = wall[(abs(wall["y-coordinate"] - 0.01) < 1e-6) & (wall["x-coordinate"] > 0.0101)]
pl = wall[(abs(wall["x-coordinate"] - 0.01) < 1e-6) & (wall["y-coordinate"] > 0.0101)]
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.0), dpi=200,
                         gridspec_kw={"width_ratios": [1.25, 1]})
ax = axes[0]
tc = ax.tricontourf(fl["z-coordinate"] * 1e3, (fl["x-coordinate"] - 0.01) * 1e3,
                    fl["skin-friction-coef"] * 1e3, levels=np.linspace(0, 5, 21), cmap=SEQ,
                    extend="max")
rev = fl["z-wall-shear"] > 0                     # wall shear opposing the main flow (-z)
ax.scatter(fl.loc[rev, "z-coordinate"] * 1e3, (fl.loc[rev, "x-coordinate"] - 0.01) * 1e3,
           s=0.6, color=C1, label="reversed wall shear (separation)")
ax.set_xlim(230, -230)
ax.set_xlabel("z (mm)   flow →   (LE at +230, TE at −230)")
ax.set_ylabel("Distance from plate along floor (mm)")
ax.set_title("(a) Skin friction on the floor (inside face)", loc="left", fontsize=7.5)
ax.legend(loc="upper right", fontsize=6, frameon=False, markerscale=4)
cb = fig.colorbar(tc, ax=ax, pad=0.01)
cb.set_label("C_f × 10³")

ax = axes[1]
bins = np.r_[0:20:2, 20:60:5, 60:200:20, 200:261:30] * 1e-3
print("\nCf (x1e3) vs distance from the corner wall, at stations:")
for (z0, lab), col in zip(((0.1, "z = +0.10"), (0.0, "z = 0"), (-0.2, "z = −0.20")), (C0, C1, C2)):
    for d, coord, ls, wname in ((fl, "x-coordinate", "-", "floor"), (pl, "y-coordinate", "--", "plate")):
        s = d[abs(d["z-coordinate"] - z0) < 0.01]
        dist = s[coord] - 0.01
        g = s.groupby(pd.cut(dist, bins))["skin-friction-coef"].mean()
        mid = np.array([iv.mid for iv in g.index]) * 1e3
        ax.plot(mid, g.values * 1e3, ls=ls, color=col, lw=1.2,
                label=f"{lab} m, {wname}")
        far = g.values[-3:].mean()
        print(f"{wname:5s} {lab:9s} near(0-4mm) {g.values[:2].mean()*1e3:.2f}  "
              f"peak {np.nanmax(g.values[:12])*1e3:.2f} at {mid[np.nanargmax(g.values[:12])]:.0f} mm  "
              f"far {far*1e3:.2f}")
ax.set_xscale("log")
ax.set_xlim(1, 260)
ax.set_xlabel("Distance from the other wall (mm, log scale)")
ax.set_ylabel("C_f × 10³")
ax.set_title("(b) C_f across the span: solid = floor, dashed = plate", loc="left", fontsize=7.5)
ax.grid(color=GRID, lw=0.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(fontsize=6, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.17))
fig.suptitle("Step E: wall shear near vs far from the junction (C_f = τ_w / ½ρU∞², U∞ = 36 m/s)",
             x=0.01, ha="left", fontsize=12, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig("figures/stepE_cf.png", facecolor=SURF)
plt.close(fig)
print("figures written")
