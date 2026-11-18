"""Grid Convergence Index (Celik et al. 2008, J. Fluids Eng. 130, 078001).

Mesh 1 = fine, 2 = medium, 3 = coarse. Values are means over the last 200 iterations (from the .out files).
Run: python3 gci.py
"""
import math

V = 0.5971020  # fluid volume [m^3], from Fluent /mesh/check
N = {1: 2_528_284, 2: 1_149_794, 3: 528_896}
h = {k: (V / n) ** (1 / 3) for k, n in N.items()}

data = {
    # name: (phi1 fine, phi2 medium, phi3 coarse, iterative half-range on fine)
    "cd": (0.0616489, 0.0625285, 0.0637306, 0.00003),
    "v_corner [m/s]": (28.3042, 29.5457, 33.1952, 0.254),
    "v_wake [m/s]": (25.6003, 27.1622, 28.5689, 0.111),
}

r21, r32 = h[2] / h[1], h[3] / h[2]
print(f"h1={h[1]*1e3:.2f} mm  h2={h[2]*1e3:.2f} mm  h3={h[3]*1e3:.2f} mm")
print(f"r21={r21:.3f}  r32={r32:.3f}\n")


def apparent_order(e21, e32):
    """Solve Celik eq. for p by fixed-point iteration."""
    s = math.copysign(1, e32 / e21)
    p = abs(math.log(abs(e32 / e21))) / math.log(r21)
    for _ in range(200):
        q = math.log((r21**p - s) / (r32**p - s))
        p_new = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        if abs(p_new - p) < 1e-10:
            break
        p = p_new
    return p


for name, (f1, f2, f3, it) in data.items():
    e21, e32 = f2 - f1, f3 - f2
    R = e21 / e32
    kind = ("monotonic" if 0 < R < 1 else
            "oscillatory" if R < 0 else "divergent (R>1)")
    print(f"--- {name} ---")
    print(f"phi1={f1}  phi2={f2}  phi3={f3}")
    print(f"e21={e21:+.5g}  e32={e32:+.5g}  R=e21/e32={R:.3f} -> {kind}")
    if 0 < R < 1:
        p = apparent_order(e21, e32)
        ext = (r21**p * f1 - f2) / (r21**p - 1)
        ea21 = abs((f1 - f2) / f1)
        eext21 = abs((ext - f1) / ext)
        gci21 = 1.25 * ea21 / (r21**p - 1)
        print(f"p={p:.2f}  phi_ext={ext:.5g}  e_a21={ea21*100:.2f}%  "
              f"e_ext21={eext21*100:.2f}%  GCI_fine={gci21*100:.2f}%")
        print(f"iterative noise on fine = {it/f1*100:.2f}%")
    else:
        ea21 = abs((f1 - f2) / f1)
        print(f"no asymptotic convergence; fine-medium change e_a21={ea21*100:.2f}%"
              f"  (GCI not defined; report spread)")
    print()
