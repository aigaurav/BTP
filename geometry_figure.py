"""Fig. 1: geometry, computational domain and post-processing stations (to scale).
Coordinates (Fluent): x normal to the plate, y normal to the floor, z streamwise (flow in -z).
"""
import os
import matplotlib
if os.environ.get("NO_TITLE"):
    import matplotlib.figure
    matplotlib.figure.Figure.suptitle = lambda self, *a, **k: None  # report version: caption replaces title
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

INK, MUTED, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
SOLID, BOI, ACC, ACC2 = "#52514e", "#cde2fb", "#eb6834", "#2a78d6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})

fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.3), dpi=200,
                           gridspec_kw={"width_ratios": [1, 2.6]})

# (a) cross-section looking downstream (x-y), cm
a.add_patch(Rectangle((-15, -10), 60, 50, fill=False, ec=INK, lw=1.2))
a.add_patch(Rectangle((-6, -5), 44, 40, color=BOI, lw=0, alpha=0.8))
a.add_patch(Rectangle((0, 0), 1, 32, color=SOLID))     # vertical plate
a.add_patch(Rectangle((0, 0), 32, 1, color=SOLID))     # floor plate
a.plot(1, 1, "o", ms=5, color=ACC)
a.annotate("inside corner\n(x, y) = (1, 1) cm", (1, 1), (8, 10), fontsize=8,
           arrowprops=dict(arrowstyle="-", color=ACC, lw=0.8), color=INK)
a.text(1.8, 26, "plate\n460×320×10 mm", fontsize=8)
a.text(18, -3.8, "floor plate 460×320×10 mm", fontsize=8, ha="center")
a.text(37, 33.3, "BOI", fontsize=8, color=ACC2, ha="right")
a.text(44, 38.3, "symmetry (top)", fontsize=7.5, ha="right", color=MUTED)
a.text(-14, -8.8, "symmetry (bottom, front, back)", fontsize=7.5, color=MUTED)
a.set_xlim(-16, 46); a.set_ylim(-11, 41); a.set_aspect("equal")
a.set_xlabel("x (cm)"); a.set_ylabel("y (cm)")
a.set_title("(a) Cross-section, looking downstream", loc="left", fontsize=10, color=INK)

# (b) side view (z-y), cm; flow from right (z=+100) to left (z=-100), plotted with z decreasing to the right
b.add_patch(Rectangle((-100, -10), 200, 50, fill=False, ec=INK, lw=1.2))
b.add_patch(Rectangle((-40, -5), 80, 40, color=BOI, lw=0, alpha=0.8))
b.add_patch(Rectangle((-23, 0), 46, 32, color="#9a9893", lw=0))   # plate (seen side-on)
b.add_patch(Rectangle((-23, 0), 46, 1, color=SOLID))              # floor plate edge
b.set_xlim(102, -102); b.set_ylim(-12, 44)
for z, lab in ((20, "+20"), (10, "+10"), (0, "0"), (-20, "−20")):
    b.plot([z, z], [-5, 36], ls="--", lw=0.9, color=ACC)
    b.text(z, 37, lab, ha="center", fontsize=7.5, color=ACC)
b.text(0, 41, "cross-planes (z, cm)", ha="center", fontsize=8, color=ACC)
for z in (0, -35):
    b.plot(z, 2, "s", ms=4, color=ACC2)
b.text(-35, 4, "v_wake", fontsize=7.5, color=ACC2, ha="center")
b.text(0, 4, "v_corner", fontsize=7.5, color=ACC2, ha="center")
b.annotate("", (60, 20), (95, 20), arrowprops=dict(arrowstyle="->", lw=1.5, color=INK))
b.text(78, 22, "U∞ = 36 m/s", ha="center", fontsize=8.5)
b.text(98, -8.5, "inlet z = +100", fontsize=7.5, color=MUTED)
b.text(-98, -8.5, "outlet z = −100 (p = 0)", fontsize=7.5, color=MUTED, ha="right")
b.text(23, -3, "LE z = +23", fontsize=7.5, ha="center")
b.text(-23, -3, "TE z = −23", fontsize=7.5, ha="center")
b.set_aspect("equal")
b.set_xlabel("z (cm)   (flow →)"); b.set_ylabel("y (cm)")
b.set_title("(b) Side view of the domain (plate shaded; BOI = refinement body)", loc="left",
            fontsize=10, color=INK)
for ax in (a, b):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig("figures/geometry_domain.png", facecolor=SURF)
print("saved")
