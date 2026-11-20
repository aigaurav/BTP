"""Conceptual animation of wall-plate junction flow (schematic model, NOT CFD data).

Coordinates (normalised): x streamwise, y normal to the plate, z normal to the wall.
Plate: y = 0, 0 <= x <= 1, 0 <= z <= H.  Wall: z = 0.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

OUT = sys.argv[1]
FPS = 30
BG = "#0f172a"
FG = "#e2e8f0"
MUTED = "#94a3b8"
ACC = "#f59e0b"   # orange: junction
CY = "#38bdf8"    # cyan: far field
H = 0.6
X0, X1 = -0.4, 2.2
rng = np.random.default_rng(1)

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": FG,
                     "axes.labelcolor": FG, "xtick.color": MUTED, "ytick.color": MUTED})

# ---------------------------------------------------------------- model field
def f(s):
    return np.clip(s, 1e-4, 1.0) ** (1 / 6)

def delta_w(x):
    return 0.06 + 0.02 * (x - X0)

def delta_p(x):
    return 0.10 * np.clip(x, 1e-3, 1.0) ** 0.8

def S(x):
    """strength of the corner effect along x (grows along plate, decays in wake)"""
    s = np.clip(x / 0.4, 0, 1)
    s = s * s * (3 - 2 * s)
    return np.where(x <= 1, s, np.exp(-(x - 1) / 1.2))

def plate_factor(x, y):
    fp = f(y / delta_p(x))
    fp1 = f(y / delta_p(1.0))
    wake = 1 - (1 - fp1) * np.exp(-(np.maximum(x, 1) - 1) / 0.8)
    return np.where(x <= 0, 1.0, np.where(x <= 1, fp, wake))

def bulge(y, z, beta):
    return 1 + beta * np.exp(-((y - z) ** 2) / (2 * 0.06 ** 2)) * np.exp(-(y + z) / 0.25)

def u_field(x, y, z, beta=1.6):
    m = bulge(y, z, beta * S(x))
    pf = np.where(x <= 0, 1.0, plate_factor(x, m * y))
    return f(m * z / delta_w(x)) * pf

R = 0.11
def psi_vw(y, z):
    """corner vortex pair: flow toward corner along bisector, out along walls"""
    E = np.exp(-(y ** 2 + z ** 2) / R ** 2)
    v = (y ** 2 * (3 * z ** 2 - 2 * y * z) + y ** 2 * z ** 2 * (z - y) * (-2 * z / R ** 2)) * E
    w = -(z ** 2 * (2 * y * z - 3 * y ** 2) + y ** 2 * z ** 2 * (z - y) * (-2 * y / R ** 2)) * E
    return -v, -w

_g = np.linspace(0, 0.4, 200)
_Y, _Z = np.meshgrid(_g, _g)
_v, _w = psi_vw(_Y, _Z)
SEC_NORM = 0.16 / np.max(np.hypot(_v, _w))   # exaggerated secondary speed (0.16 U)

SEC = {"mult": 1.0, "decay": 1.2}
def vel(p, beta=1.6):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    u = u_field(x, y, z, beta)
    v, w = psi_vw(y, z)
    ramp = np.clip(x / 0.15, 0, 1)
    sx = np.where(x <= 1, ramp, np.exp(-(x - 1) / SEC["decay"]))
    s = sx * SEC_NORM * SEC["mult"] * np.exp(-((y ** 2 + z ** 2) / 0.19 ** 2) ** 3)
    return np.stack([u, s * v, s * w], axis=1)

def step(p, dt):
    k1 = vel(p)
    k2 = vel(p + 0.5 * dt * k1)
    q = p + dt * k2
    q[:, 1] = np.clip(q[:, 1], 0.004, None)
    q[:, 2] = np.clip(q[:, 2], 0.004, None)
    return q

# ---------------------------------------------------------------- drawing helpers
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)

def header(title, sub=None):
    fig.text(0.04, 0.93, title, fontsize=24, weight="bold", color=FG)
    if sub:
        fig.text(0.04, 0.885, sub, fontsize=13, color=MUTED)

def caption(lines):
    y = 0.135
    for label, txt in lines:
        fig.text(0.04, y, label, fontsize=13, weight="bold", color=ACC)
        fig.text(0.17, y, txt, fontsize=13, color=FG)
        y -= 0.04

def footer():
    fig.text(0.96, 0.015, "Schematic animation (simplified model, not to scale) — not CFD output",
             fontsize=9, color=MUTED, ha="right")

def ax3d(rect, xlim, ylim, zlim, aspect, elev, azim, zoom=1.0):
    ax = fig.add_axes(rect, projection="3d", facecolor=BG)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_zlim(*zlim)
    ax.set_box_aspect(aspect, zoom=zoom)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.computed_zorder = False
    return ax

def draw_geometry(ax, xlim, ylim, zmax):
    wall = [[(xlim[0], ylim[0], 0), (xlim[1], ylim[0], 0), (xlim[1], ylim[1], 0), (xlim[0], ylim[1], 0)]]
    ax.add_collection3d(Poly3DCollection(wall, facecolor="#334155", edgecolor="#475569", alpha=0.85))
    zt = min(H, zmax)
    plate = [[(0, 0, 0), (1, 0, 0), (1, 0, zt), (0, 0, zt)]]
    ax.add_collection3d(Poly3DCollection(plate, facecolor="#64748b", edgecolor="#cbd5e1", alpha=0.45))
    ax.plot([0, 1], [0, 0], [0, 0], color=ACC, lw=2.5)  # the junction line

def axis_labels(ax, x, y, z):
    ax.text(*x, "x  (flow)", color=MUTED, fontsize=10)
    ax.text(*y, "y", color=MUTED, fontsize=10)
    ax.text(*z, "z", color=MUTED, fontsize=10)

cmap = plt.get_cmap("plasma")
frames = []  # list of (scene_fn, local_frame, n)

# ---------------------------------------------------------------- scenes
def scene_title(i, n):
    a = min(1, i / 20)
    fig.text(0.5, 0.60, "Flow at a Wall–Plate Junction", fontsize=36, weight="bold",
             ha="center", color=FG, alpha=a)
    fig.text(0.5, 0.52, "How the two boundary layers meet, twist and mix at the corner",
             fontsize=17, ha="center", color=MUTED, alpha=a)
    fig.text(0.5, 0.40, "1  Incoming boundary layers     2  Vortex lines bend at the corner\n"
             "3  Secondary flow in the corner     4  Helical motion along the junction",
             fontsize=14, ha="center", color=FG, alpha=a, linespacing=1.8)
    footer()

# scene 1: incoming flow, particles coloured by speed
S1_N = 900
s1 = {}
def scene1_init():
    s1["p"] = np.empty((0, 3))
def scene1(i, n):
    if i == 0:
        scene1_init(); SEC["mult"], SEC["decay"] = 1.0, 1.2
    p = s1["p"]
    new = np.column_stack([np.full(14, X0), rng.uniform(0.005, 0.55, 14),
                           0.55 * rng.uniform(0, 1, 14) ** 1.6 + 0.004])
    p = np.vstack([p, new])
    for _ in range(2):
        p = step(p, 0.012)
    p = p[p[:, 0] < X1]
    s1["p"] = p
    header("1 · Two boundary layers approach the corner",
           "Fluid slows down next to every no-slip surface")
    azim = -62 + 14 * i / n
    ax = ax3d([-0.05, 0.16, 1.0, 0.77], (X0, X1), (0.6, 0), (0, 0.6), (2.6, 0.9, 0.8), 20, azim, 1.45)
    draw_geometry(ax, (X0, X1), (0, 0.6), 0.6)
    spd = vel(p)[:, 0]
    ax.scatter(p[:, 0], p[:, 1], p[:, 2], c=spd, cmap=cmap, vmin=0.3, vmax=1, s=5, depthshade=False)
    # inlet wall-BL profile
    zz = np.linspace(0.005, 0.25, 9)
    uu = f(zz / delta_w(-0.35)) * 0.35
    ax.quiver(np.full(9, -0.38), np.full(9, 0.45), zz, uu, 0 * zz, 0 * zz, color=FG, lw=1.2,
              arrow_length_ratio=0.15)
    # plate-BL profile on the plate
    yy = np.linspace(0.004, 0.15, 7)
    up = f(yy / delta_p(0.9)) * 0.35
    ax.quiver(np.full(7, 0.6), yy, np.full(7, 0.45), up, 0 * yy, 0 * yy, color=FG, lw=1.2,
              arrow_length_ratio=0.15)
    ax.text(0.3, 0.0, 0.64, "plate", color=FG, fontsize=12)
    ax.text(1.7, 0.6, 0.0, "wall", color=FG, fontsize=12)
    ax.text(1.05, 0.0, 0.02, "← junction (corner)", color=ACC, fontsize=12)
    ax.text(-0.4, 0.45, 0.3, "flow →", color=FG, fontsize=13)
    cax = fig.add_axes([0.92, 0.30, 0.012, 0.35])
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0.3, 1)), cax=cax)
    cb.set_label("u / U∞", color=FG); cb.outline.set_edgecolor(MUTED)
    caption([("What we see", "Slow fluid (dark) hugs the wall and the plate; fast fluid (yellow) further away."),
             ("Why", "No-slip: u = 0 on both surfaces → wall BL u(z) and plate BL u(y)."),
             ("Mechanism", "In the corner the fluid feels BOTH surfaces at once — slowest region of all.")])
    footer()

# scene 2: vortex lines bending at the corner
def vortex_line(xc, tilt, y0=0.04, z0=0.04, rc=0.07, L=0.55, n=160):
    s_wall = np.linspace(0, 1, n)
    ys = np.concatenate([np.linspace(L, y0 + rc, n),
                         y0 + rc - rc * np.sin(np.linspace(0, np.pi / 2, n)),
                         np.full(n, y0)])
    zs = np.concatenate([np.full(n, z0),
                         z0 + rc - rc * np.cos(np.linspace(0, np.pi / 2, n)),
                         np.linspace(z0 + rc, L, n)])
    # distance from corner -> lag of the bend (corner fluid is slowest)
    d = np.hypot(ys - y0, zs - z0)
    xs = xc - tilt * np.exp(-(d / 0.12) ** 2)
    return xs, ys, zs

def scene2(i, n):
    header("2 · Vortex lines cannot end, so they bend at the corner",
           "Wall BL carries ω_y (spanwise), plate BL carries ω_z (vertical)")
    ax = ax3d([0.0, 0.17, 0.62, 0.72], (-0.1, 1.4), (0, 0.6), (0, 0.6), (1.5, 0.75, 0.7), 22, 52, 1.2)
    draw_geometry(ax, (-0.1, 1.4), (0, 0.6), 0.6)
    t = i / n
    for k in range(4):
        tt = (t * 1.6 - k * 0.38)
        if tt < 0:
            continue
        tt = min(tt, 1.0) if k < 3 else min(tt, 1.0)
        xc = 0.05 + 1.1 * tt
        tilt = 0.32 * S(np.array(xc)) * min(1, tt * 1.5)
        xs, ys, zs = vortex_line(xc, tilt)
        pts = np.column_stack([xs, ys, zs])
        seg = np.stack([pts[:-1], pts[1:]], axis=1)
        dx = np.abs(np.diff(xs)); ds = np.linalg.norm(np.diff(pts, axis=0), axis=1) + 1e-12
        frac = np.clip(dx / ds * 2.2, 0, 1)
        cols = plt.get_cmap("coolwarm")(0.15 + 0.85 * frac)
        lc = Line3DCollection(seg, colors=cols, linewidths=3)
        ax.add_collection3d(lc)
    ax.text(0.0, 0.58, 0.06, "ω_y on the wall", color="#93c5fd", fontsize=11)
    ax.text(0.0, 0.0, 0.62, "ω_z on the plate", color="#93c5fd", fontsize=11)
    # right-hand text panel
    tx = 0.63
    fig.text(tx, 0.74, "Two rules", fontsize=16, weight="bold", color=ACC)
    fig.text(tx, 0.665, "1. ∇·ω = 0 → a vortex line can't end\n    inside the fluid",
             fontsize=13, color=FG, linespacing=1.4)
    fig.text(tx, 0.585, "2. On a no-slip surface, vortex lines\n    lie flat on that surface",
             fontsize=13, color=FG, linespacing=1.4)
    if t > 0.35:
        fig.text(tx, 0.49, "So the line must turn 90° at the corner.", fontsize=13, color=FG)
    if t > 0.5:
        fig.text(tx, 0.36, r"$\dfrac{\partial\omega_x}{\partial x}=-\left(\dfrac{\partial\omega_y}{\partial y}"
                 r"+\dfrac{\partial\omega_z}{\partial z}\right)\neq 0$", fontsize=17, color=FG)
    if t > 0.6:
        fig.text(tx, 0.31, "The corner fluid is slowest, so the bend\nlags behind → the line tilts in x\n"
                 "→ streamwise vorticity ω_x (red).", fontsize=13, color=FG, linespacing=1.4, va="top")
    caption([("What we see", "Blue = vorticity across the flow (ω_y, ω_z); red = streamwise vorticity ω_x."),
             ("Why", "The wall's ω_y lines must connect to the plate's ω_z lines through the corner."),
             ("Mechanism", "Bending + slower corner fluid tilts the line → ω_x is generated near the junction.")])
    footer()

# scene 3: cross-plane at x = 0.7
s3 = {}
def scene3(i, n):
    if i == 0:
        q = rng.uniform(0.008, 0.21, (900, 2))
        s3["p"] = q[np.hypot(q[:, 0], q[:, 1]) < 0.21][:300]
    header("3 · Secondary flow in the corner (cross-plane at mid-plate)",
           "Looking along the flow: plate on the left, wall at the bottom")
    g = np.linspace(0.0, 0.22, 160)
    Y, Z = np.meshgrid(g, g)
    xs = 0.7
    beta = 1.6 * min(1, i / (0.4 * n))
    levels = np.linspace(0.3, 1.0, 15)
    for j, (rect, b, ttl) in enumerate([([0.06, 0.22, 0.36, 0.6], 0.0, "Without secondary flow\n(two boundary layers simply merge)"),
                                        ([0.50, 0.22, 0.36, 0.6], beta, "With secondary flow (ω_x)\n(fluid circulates in the corner)")]):
        ax = fig.add_axes(rect, facecolor=BG)
        m = bulge(Y, Z, b)
        U = f(m * Z / delta_w(xs)) * f(m * Y / delta_p(xs))
        ax.contourf(Y, Z, U, levels=levels, cmap=cmap, extend="both")
        ax.contour(Y, Z, U, levels=[0.6, 0.7, 0.8, 0.9], colors="white", linewidths=0.8, alpha=0.7)
        ax.plot([0, 0], [0, 0.22], color="#cbd5e1", lw=6)
        ax.plot([0, 0.22], [0, 0], color="#cbd5e1", lw=6)
        ax.set_xlim(0, 0.22); ax.set_ylim(0, 0.22); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_xlabel("y  (away from plate)  →", fontsize=11)
        ax.set_ylabel("z  (away from wall)  →", fontsize=11)
        ax.set_title(ttl, fontsize=13, color=FG)
        ax.text(0.005, 0.21, "plate", rotation=90, color=BG, fontsize=10, va="top")
        ax.text(0.21, 0.003, "wall", color=BG, fontsize=10, ha="right")
        if j == 1:
            p = s3["p"]
            ramp = min(1, i / (0.3 * n))
            for _ in range(6):
                v, w = psi_vw(p[:, 0], p[:, 1])
                k1 = np.column_stack([v, w])
                v, w = psi_vw(p[:, 0] + 0.012 * SEC_NORM * ramp * k1[:, 0], p[:, 1] + 0.012 * SEC_NORM * ramp * k1[:, 1])
                p = p + 0.025 * SEC_NORM * ramp * np.column_stack([v, w])
            p = np.clip(p, 0.003, 0.22)
            s3["p"] = p
            ax.scatter(p[:, 0], p[:, 1], s=6, color="white", alpha=0.9)
            gq = np.linspace(0.015, 0.205, 11)
            QY, QZ = np.meshgrid(gq, gq)
            qv, qw = psi_vw(QY, QZ)
            ax.quiver(QY, QZ, qv, qw, color="#a5f3fc", scale=np.max(np.hypot(qv, qw)) * 12, width=0.004,
                      alpha=min(1, i / (0.3 * n)))
    cax = fig.add_axes([0.89, 0.30, 0.012, 0.42])
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0.3, 1)), cax=cax)
    cb.set_label("u / U∞ (isovels)", color=FG); cb.outline.set_edgecolor(MUTED)
    caption([("What we see", "With secondary flow the isovels bulge into the corner; tracers circulate in two cells."),
             ("Why", "ω_x from the bent vortex lines = rotation about the flow direction → in-plane v, w."),
             ("Mechanism", "Fast fluid is carried into the corner, slow fluid out along the walls → the BLs mix.")])
    footer()

# scene 4: helical paths along the junction vs far field
s4 = {}
TRAIL = 75
def scene4(i, n):
    if i == 0:
        SEC["mult"], SEC["decay"] = 3.2, 1.6
        s4["hist"] = []
        s4["p"] = np.empty((0, 3)); s4["kind"] = np.empty(0)
    p, kind = s4["p"], s4["kind"]
    if i % 4 == 0 and i < n * 0.75:
        a = rng.uniform(0, 2 * np.pi, 5)
        r = rng.uniform(0.025, 0.05, 5)
        c = np.where(rng.uniform(size=5) < 0.5, 0, 1)
        cy = np.where(c == 0, 0.156, 0.078); cz = np.where(c == 0, 0.078, 0.156)
        corner = np.column_stack([np.full(3, -0.05), (cy + r * np.cos(a))[:3], (cz + r * np.sin(a))[:3]])
        far = np.column_stack([np.full(1, -0.05), rng.uniform(0.22, 0.25, 1), rng.uniform(0.03, 0.08, 1)])
        p = np.vstack([p, corner, far]); kind = np.concatenate([kind, np.zeros(3), np.ones(1)])
    p = step(p, 0.02)
    keep = p[:, 0] < 2.0
    s4["hist"].append(p.copy())
    s4["hist"] = s4["hist"][-TRAIL:]
    s4["p"], s4["kind"] = p, kind
    header("4 · Along the junction: fluid spirals downstream",
           "Corner fluid (orange) vs fluid far from the plate (cyan); y and z stretched to show the corner")
    azim = -58 + 14 * i / n
    ax = ax3d([-0.05, 0.16, 1.0, 0.77], (-0.15, 2.0), (0.26, 0), (0, 0.26), (2.4, 1.0, 0.9), 22, azim, 1.45)
    draw_geometry(ax, (-0.15, 2.0), (0, 0.26), 0.26)
    hist = s4["hist"]
    npnow = len(p)
    for idx in range(npnow):
        pts = [h[idx] for h in hist if len(h) > idx]
        pts = np.array(pts)
        if len(pts) < 2 or pts[-1, 0] > 2.0 or pts[-1, 1] > 0.26 or pts[-1, 2] > 0.26:
            continue
        col = ACC if kind[idx] == 0 else CY
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=col, lw=1.6, alpha=0.9)
    ax.text(0.35, 0.0, 0.28, "plate", color=FG, fontsize=12)
    ax.text(1.05, 0.0, 0.29, "behind the plate →", color=MUTED, fontsize=12)
    caption([("What we see", "Corner fluid follows helical paths; far-field fluid travels straight."),
             ("Why", "Streamwise vorticity ω_x is concentrated at the junction and is advected downstream."),
             ("Mechanism", "Behind the plate (x > L) ω_x decays → the corner flow and wake gradually recover.")])
    footer()

def scene_end(i, n):
    a = min(1, i / 20)
    fig.text(0.5, 0.66, "Summary", fontsize=30, weight="bold", ha="center", color=FG, alpha=a)
    fig.text(0.5, 0.36,
             "No-slip on wall and plate  →  two boundary layers (ω_y and ω_z)\n"
             "∇·ω = 0  →  vortex lines bend at the corner  →  streamwise vorticity ω_x\n"
             "ω_x  →  secondary flow in the corner  →  mixing of the two boundary layers\n"
             "Behind the plate  →  ω_x decays and the junction flow recovers",
             fontsize=16, ha="center", color=FG, alpha=a, linespacing=2.0)
    fig.text(0.5, 0.18, "Compare with CFD: ω_x contours, in-plane vectors and pathlines at the junction",
             fontsize=13, ha="center", color=ACC, alpha=a)
    footer()

plan = [(scene_title, 4), (scene1, 11), (scene2, 12), (scene3, 12), (scene4, 13), (scene_end, 5)]
total = sum(int(d * FPS) for _, d in plan)
writer = FFMpegWriter(fps=FPS, bitrate=3500, codec="libx264", extra_args=["-pix_fmt", "yuv420p"])
k = 0
with writer.saving(fig, OUT, dpi=100):
    for fn, dur in plan:
        n = int(dur * FPS)
        for i in range(n):
            fig.clear()
            fig.set_facecolor(BG)
            fn(i, n)
            writer.grab_frame(facecolor=BG)
            k += 1
            if k % 60 == 0:
                print(f"{k}/{total}", flush=True)
print("done")
