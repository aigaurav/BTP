# BTP project log: wall–plate junction flow (L-shaped model)

Running record of every decision and number, used to write the final report.
Update after every stage.

---

## 1. Geometry (DesignModeler, unchanged by decision of the student)

Two thin plates joined in an L, placed in a free stream; the study region is the inside corner
(junction) where the floor-plate and vertical-plate boundary layers meet and mix.

| Item | Value |
|---|---|
| Vertical plate | 460 mm long (z, flow direction) × 320 mm high (y) × 10 mm thick (x) |
| Floor plate | 460 mm long (z) × 320 mm wide (x) × 10 mm thick (y) |
| L position | z = −0.23 … +0.23 m; outer corner at origin; floor plate y = 0 … 0.01 m |
| Inside corner of the L | x = 0.01 m, y = 0.01 m (runs along z) |
| Enclosure (fluid) | x −0.15 … 0.45, y −0.10 … 0.40, z −1.0 … 1.0 m (0.60 × 0.50 × 2.0 m) |
| BOI (body of influence) | x −0.06 … 0.38, y −0.05 … 0.35, z −0.40 … 0.40 m |
| Flow direction | −z (inlet at z = +1, outlet at z = −1) |
| Leading / trailing edge of plates | z = +0.23 / z = −0.23 m |
| DM sketches | Sketch1 (L section, XY): H2 32, V1 32, H4 1, V3 1 cm; Extrude1 frozen, symmetric 23 cm |
| | Sketch2 (enclosure, ZX): H3 100, H4 100, V1 45, V2 15 cm; Extrude2 +40 / −10 cm |
| | Sketch3 (BOI, ZX): H5 40, H6 40, V7 38, V8 6 cm; Extrude3 frozen +35 / −5 cm |

Named selections: model (8 faces of the L), inlet, outlet, front wall, back wall, top wall,
bottom wall (appears in Fluent as `bottam_wall`).

Estimates: Re_L = 36 × 0.46 / 1.46e-5 ≈ 1.1e6; turbulent δ at trailing edge ≈ 10 mm;
u_τ ≈ 1.5 m/s → first cell for y⁺ ≈ 1 ≈ 0.01 mm. Blockage of the L ≈ 2 % of the cross-section.

## 2. Mesh: FINE (Ansys Meshing 2024 R1)

| Setting | Value |
|---|---|
| Physics / solver preference | CFD / Fluent |
| Global element size | 50 mm |
| Face sizing (8 faces of L) | 5 mm, capture proximity off |
| Body of influence sizing | 12 mm |
| Inflation (on L faces, in fluid body) | first layer 0.01 mm, 25 layers, growth 1.2 (≈ 4.7 mm total) |
| Nodes / elements | 848,165 / 2,528,284 (tet + wedge) |
| Skewness max / avg | 0.800 / 0.216 |
| Orthogonal quality min / avg | 0.0062 (Meshing), 0.00644 (Fluent) / 0.764 |
| Low-quality cells | 2,660 cells (0.1 %) below 0.0156, at outer free edge of floor plate (x ≈ 0.318 m), far from junction |
| Max aspect ratio | 2855 (inflation prisms, expected) |
| Fluent `improve-quality` | no change; accepted |
| Previous attempt | 24.2 M elements (too fine), replaced by this mesh |

## 3. Fluent setup (2024 R1, double precision, 16 processes)

| Item | Setting |
|---|---|
| Solver | Pressure-based, steady |
| Turbulence | k-ω SST (defaults) |
| Fluid | air, ρ = 1.225 kg/m³, μ = 1.7894e-5 kg/m·s; cell zone type fluid |
| inlet | velocity-inlet, 36 m/s normal; I = 1 %, μt/μ = 10 |
| outlet | pressure-outlet, 0 Pa; backflow I = 5 %, μt/μ = 10 |
| front/back/top/bottom wall | symmetry |
| model | no-slip wall |
| Reference values | from inlet (36 m/s, 1.225); area 0.1472 m² (0.46 × 0.32); length 0.46 m |
| Scheme | Coupled, pseudo-time ON (explicit relaxation p 0.5, mom 0.5, k/ω 0.75); time step auto, length scale conservative |
| Spatial | LSQ cell-based gradients; 2nd-order pressure; 2nd-order upwind momentum, k, ω |
| Init | Hybrid |
| Residual criteria | 1e-6 (so run does not stop early) |

Monitors:

| Name | Definition |
|---|---|
| cd | Drag coefficient on `model`, force vector (0, 0, −1) |
| p_corner / v_corner | Point (0.02, 0.02, 0): 10 mm from both plates, mid-length; facet-average velocity magnitude |
| p_wake / v_wake | Point (0.02, 0.02, −0.35): corner wake 0.26 L behind trailing edge (inside BOI); same report |

Point creation TUI: `/surface/point-surface p_corner 0.02 0.02 0`.

## 4. Run log: fine mesh

- Iterations 1–162 were run with default reference values (U = 1 m/s, A = 1 m²), so cd was printed as 11.76.
  The equivalent drag force is ≈ 7.2 N, giving true cd ≈ 0.062. The reference values were corrected at
  iteration ~162 and the run continued without re-initialisation. **Plot cd only from after the fix.**
- At iteration 162: residuals flat (continuity ≈ 3.7e-3, velocities ≈ 5e-7 to 2e-6, k ≈ 1.7e-3, ω ≈ 3.2e-4).
  v_corner ≈ 28.3 m/s (oscillating 28.0–28.5), v_wake ≈ 25.5 m/s, cd flat. About 7.7 s per iteration.
- Decision: stop at about 500 iterations once the monitors are flat. Proof needed: Δ < 0.1 % between iterations
  300 and 500, mass imbalance < 0.1 %, optional +100 iterations showing no change.

Run finished at iteration 501, about 7.7 s per iteration on 16 processes.

| Quantity | It. 300 | It. 500 | Change 300→500 | Min / max over 300–501 | Mean ± half-range | Verdict |
|---|---|---|---|---|---|---|
| cd | 0.061645 | 0.061644 | 0.002 % | 0.061618 / 0.061678 | **0.06165 ± 0.00003 (±0.05 %)** | converged |
| v_corner [m/s] | 28.435 | 28.166 | −0.9 % (phase of oscillation) | 28.029 / 28.536 | **28.28 ± 0.25 (±0.9 %)** | bounded oscillation, no drift |
| v_wake [m/s] | 25.515 | 25.546 | +0.1 % | 25.471 / 25.693 | **25.58 ± 0.11 (±0.4 %)** | bounded oscillation, no drift |
| Mass flow in / out [kg/s] | | 13.23 / −13.22998 | net 2.15e-5 kg/s (0.00016 %) | | | conserved |

Stage 1 checks (iteration 501):

| Check | Result | Verdict |
|---|---|---|
| Inlet mass flow | 13.23 kg/s (= 1.225 × 36 × 0.6 × 0.5, matches) | ✓ |
| Mass imbalance | 2.15e-5 kg/s = 0.00016 % | ✓ |
| y⁺ on model | area-weighted avg 0.42, facet max 0.93 | ✓ y⁺ < 1 everywhere |
| Max velocity (domain) | 66.27 m/s = 1.84 U∞ | ⚠ investigate location (sharp 10 mm leading-edge corners or poor cells at x ≈ 0.318?) |
| Max static pressure on model | 868.6 Pa vs ½ρU² = 793.8 Pa | ⚠ check against inlet total pressure (inlet static > 0 because outlet is the 0 Pa reference) |

- Residuals over 300–501: continuity 3.2–3.8e-3, velocities ≈ 5e-7 / 2e-6, k ≈ 1.5–1.8e-3, ω ≈ 3e-4.
  They oscillate with no trend, so they have plateaued.
- v_corner and v_wake oscillate with a period of about 20–40 iterations and constant amplitude. Possible causes are weak
  unsteadiness of the corner flow or the steady-RANS pseudo-time iteration. Report the mean ± half-range.
- **Iterative uncertainty:** ±0.9 % for v_corner and ±0.4 % for v_wake. In the grid study, differences between meshes
  smaller than this cannot be resolved, so use the mean over the last 200 iterations for every mesh.
- Monitor files (`cd-rfile.out`, `v_corner-rfile.out`, `v_wake-rfile.out`) are in
  `\\netapp2...\Downloads\14\bbttpp_14_files\dp0\FFF\Fluent\` (project `bbttpp_14.wbpj`, stored on the college network drive in Downloads).

Stage 1 checks still to do: y⁺ on model (average and maximum), maximum velocity, maximum pressure on model (~794 Pa),
mass balance.

Leading-edge peaks: located with iso-surfaces iso_v42 (velocity 42 m/s) and iso_p819 (static pressure 819 Pa).
- Node-averaged maxima: velocity 44.6 m/s (1.24 U∞), static pressure 836.9 Pa vs inlet total pressure 818.8 Pa
  (+2 %, a normal 2nd-order overshoot at a sharp stagnation point). Node minimum pressure −915 Pa (suction peak at the sharp edges).
- Inlet: static pressure 25.0 Pa, total pressure 818.8 Pa (area-weighted average).
- iso_p819 sits on the blunt 10 mm front face; the **largest stagnation blob is at the inside corner of the front
  face** (fluid blocked by both plates), which is the start of the junction flow (Step C).
- iso_v42 forms thin sheets just outside the sharp front edges on both sides of each plate: acceleration around the
  sharp corners, followed by a small separation bubble.
- Single-cell spikes (66.3 m/s, 868.6 Pa) are sharp-edge singularities. They are not at the poor-quality cells and
  do not affect cd or the monitors. **Stage 1 complete.**

## 4a. Figures saved (for the report)

Folder: **`C:\Users\am1230752\BTP_images\`** (local disk). Fluent's Save Picture fails on the `\\netapp2...` network path
("error opening PNG file"), so always give the full local path. Copy the folder to Google Drive or a pen drive at the end of
every session, because local profile folders on college computers may be wiped at logout.
Naming rule: `mesh_quantity_location.png`, 1920 × 1080, white background.

| File | Content | Report section |
|---|---|---|
| `fine_LE_iso_p819_v42.png` | Front view of the L with iso_p819 + iso_v42 (leading-edge stagnation and edge acceleration) | Stage 1 checks / Step C |

## 5. Decisions and justifications (for the report and viva)

- Geometry kept as the free-standing L (two plates). Both boundary layers start at the same leading edge, so there
  is no thick incoming wall boundary layer as in Nakayama & Rahai (1984). The comparison with them is therefore
  qualitative (trends), and a strong horseshoe vortex is not expected.
- Mesh reduced from 24.2 M to 2.53 M elements: proper face sizing, BOI and inflation with y⁺ ≈ 1.
- SIMPLE (mid-sem, under-relaxation 0.1/0.2) replaced by Coupled with pseudo-transient relaxation, for faster and
  more robust convergence on the high-aspect-ratio inflation mesh.
- Convergence is judged by monitors (< 0.1 % over 200 iterations), flat residuals and mass balance, not by iteration
  count. The answer for "why only 500 iterations" is in the session notes: Coupled needs 3–5× fewer iterations than SIMPLE.
- Report v_corner as mean ± amplitude over the last 200 iterations (slow ±1 % oscillation, possibly weak unsteadiness of the corner flow).

## 6. Remaining plan

1. **Stage 1:** finish the fine run; y⁺, maximum velocity, maximum pressure, mass balance; save the project.
2. **Stage 2 (grid study):** duplicate the system. Medium: face 6.5 mm, BOI 15.6 mm. Coarse: face 8.5 mm, BOI 20 mm.
   Inflation and setup identical. Run each until the monitors are flat. Collect cd, v_corner and v_wake, then
   calculate GCI (Celik 2008). Overlay the corner velocity profile for all three meshes.
3. **Stage 3 (junction physics, fine mesh):**
   - A: boundary-layer profiles far from vs near the corner
   - B: vorticity and ∇·ω = 0 at the corner
   - C: leading-edge region of the corner (wall shear, pathlines)
   - D: isovels and secondary-flow vectors on cross-planes z = +0.1, 0, −0.2, zoomed to about 40 × 40 mm at the corner
   - E: wake recovery along the corner line, and wall shear near vs far from the plate
4. **Stage 4 (optional):** SST Corner Flow Correction, restarted from the fine solution, or RSM; compare with plain SST.
5. **Final report and slides:**
   1. Introduction
   2. Mid-sem problems and fixes
   3. Geometry and mesh
   4. Setup
   5. Convergence
   6. Grid independence and GCI
   7. Junction physics, Steps A–E
   8. Qualitative comparison with Nakayama & Rahai
   9. Limitations and future work (XFLR5 NACA 0010 wing–body junction)

## 7. Stage 2: grid study meshes

Same geometry, inflation (0.01 mm, 25 layers, 1.2), global size 50 mm, BCs and solver settings. Only face sizing and BOI change.
Effective ratio r = (N_fine / N_coarser)^(1/3), target ≈ 1.3 (Celik et al. 2008).

| Mesh | Face sizing | BOI | Nodes | Elements | Max skew | Min OQ | r vs finer |
|---|---|---|---|---|---|---|---|
| Fine (A) | 5 mm | 12 mm | 848,165 | 2,528,284 | 0.800 | 0.0062 | n/a |
| Medium, first try (rejected) | 6.5 mm | 15.6 mm | 500,663 | 1,448,353 | 0.799 | 0.0069 | 1.20 (too small) |
| **Medium (B)** | **7.3 mm** | **17.5 mm** | 403,363 | **1,149,794** | n/a | 0.0070 | **1.300** |
| **Coarse (C)** | **10.6 mm** | **25.5 mm** | 184,203 | **528,896** | 0.796 | 0.0047 | **1.296** |

Note: element count scales roughly as h^-2.1 here (not h^-3), because the inflation prisms (fixed layer count) are a large share of the mesh.

### Medium mesh results (B, 1.15 M, iterations 485–500)

| Quantity | Medium | Fine | Medium vs fine |
|---|---|---|---|
| cd | 0.06253 (±0.00001) | 0.06165 | +1.4 % |
| v_corner [m/s] | 29.54 (±0.01, flat) | 28.28 ± 0.25 | +4.5 % |
| v_wake [m/s] | 27.16 (flat) | 25.58 ± 0.11 | +6.2 % |
| Residuals | continuity 2.6e-4, velocities ~1e-7/3e-7, k 2.5e-4, ω 1.3e-4 | | |

- The medium mesh converges to a steady state with no oscillation. The fine mesh shows a ±0.9 % oscillation at the corner,
  so the finer mesh starts to resolve slight unsteadiness that the coarser mesh damps numerically.
- The corner point values change 4–6 % between medium and fine, much more than the iteration noise. The corner region is
  the hardest to resolve, because the points sit at the edge of the ~10 mm boundary layer where the gradients are steep.
  Wait for the coarse mesh and GCI before concluding.
- Medium checks: y⁺ on model average 0.414, maximum 0.920. Mass flow 13.23 in / −13.23 out, net −3.86e-6 kg/s (0.00003 %).

### Coarse mesh results (C, 0.53 M, iterations 480–500)

cd 0.06372 (±0.00002), v_corner 33.05 m/s (±0.03, shifted from ~33.4 to ~33.05 near iteration 390), v_wake 28.49 m/s (slow ±0.1 oscillation).
y⁺ on model: average 0.386, maximum 0.766. Mass: 13.23 in / −13.23 out, net −1.47e-5 kg/s (0.0001 %).

### GCI (Celik et al. 2008), calculated with `gci.py`

h = (V/N)^(1/3): h1 = 6.18 mm, h2 = 8.04 mm, h3 = 10.41 mm; r21 = 1.300, r32 = 1.295.

| Quantity | Coarse | Medium | Fine | R = ε21/ε32 | Type | p | φ_ext | e_a21 (fine vs medium) | GCI_fine |
|---|---|---|---|---|---|---|---|---|---|
| cd | 0.06372 | 0.06253 | 0.06165 | 0.74 | monotonic | 1.22 | 0.0593 | **1.43 %** | **4.7 %** |
| v_corner [m/s] | 33.05 | 29.54 | 28.28 | 0.36 | monotonic | 3.97 | 27.59 | 4.47 % | **3.0 %** |
| v_wake [m/s] | 28.49 | 27.16 | 25.58 | 1.19 | **divergent** | n/a | n/a | 6.18 % | not defined |

Interpretation:
- cd: medium→fine change 1.43 % (< 2 % target), monotonic convergence. GCI_fine 4.7 % → cd = 0.0617 ± 0.0029.
  The apparent order of 1.22 is below the formal 2nd order, typical for tet/prism meshes and sharp edges.
- v_corner: monotonic. GCI_fine 3.0 % → 28.3 ± 0.9 m/s; extrapolated value 27.6 m/s. The apparent order of 3.97 is above
  the formal order, so the GCI should be treated with caution (Celik's note on p much greater than the formal order).
  The fine→medium change (4.5 %) is larger than the 2 % target, so the corner needs the fine mesh.
- v_wake (z = −0.35, near the downstream end of the BOI): differences do not shrink (R > 1), so this location is not in the
  asymptotic range. The fine mesh also starts to resolve slight unsteadiness there. Report the spread (6 %) and use the
  fine mesh. Option: evaluate a more robust wake measure (area-averaged velocity deficit over the corner region on a
  cross-plane) on all three saved solutions. That needs no re-run.
- Conclusion for the report: Stage 3 uses the fine mesh. Global quantities are grid-independent within about 5 %. Local corner
  values carry about 3 % uncertainty. The corner wake is the most mesh-sensitive region.

## 8. Stage 3: junction physics (fine mesh)

Lines (z = 0, mid-length), created with `/surface/line-surface name x0 y0 z0 x1 y1 z1`:
floor_far (0.25, 0.01→0.06), floor_near (0.02, 0.01→0.06), plate_far (0.01→0.06, 0.25), plate_near (0.01→0.06, 0.02),
bisector (0.01, 0.01) → (0.05, 0.05).

### Step A: boundary-layer profiles (qualitative, from the plots; exact δ99 to follow from the .xy files)
- Outer (edge) velocity ≈ 37.3–37.5 m/s, about 3.5 % above U∞ because of displacement by the L.
- floor_far: δ99 ≈ 20–25 mm. plate_far: δ99 ≈ 25–27 mm. Both are much thicker than the flat-plate estimate (≈ 6 mm at
  mid-length) → likely because of the blunt 10 mm leading edge (separation at the sharp front edges, then a thick reattached BL).
- floor_near (10 mm from the plate) and plate_near (10 mm above the floor) never reach the edge velocity (≈ 33–34 m/s far
  out), because they run inside the other wall's BL: the two boundary layers overlap near the corner.
- **Bulge:** plate_near peaks at ≈ 35.3 m/s about 20 mm from the plate, then drops to ≈ 33 m/s. At 10 mm above the floor the
  velocity is ≈ 33–35 m/s near the plate vs ≈ 25 m/s far from it → high-momentum fluid is carried toward the corner along
  the diagonal (corner secondary flow). Confirm with the cross-plane isovels and vectors (Step D).
- bisector (the plot's x-axis is position = x + y): reaches the edge velocity at x + y ≈ 0.065, i.e. about 32 mm from the
  corner along the diagonal. For two independent BLs with no secondary flow, expect √2·δ ≈ 33–38 mm. Slightly less →
  consistent with the fluid being pushed into the corner.

**Step A, exact values** (`stepA_profiles.py`, data in `data/stage3/`, figure `figures/stepA_profiles.png`):

| Line | Edge u (m/s) | δ99 (mm) | δ* (mm) | θ (mm) | H = δ*/θ |
|---|---|---|---|---|---|
| floor_far | 37.35 | 25.6 | 6.12 | 3.69 | 1.66 |
| plate_far | 37.47 | 26.0 | 6.34 | 3.86 | 1.64 |
| floor_near (10 mm from plate) | max 34.52 at 23 mm, 33.2 at 50 mm | n/a (no plateau) | | | |
| plate_near (10 mm above floor) | max 35.27 at 26 mm, 33.1 at 50 mm | n/a | | | |
| bisector | 37.54 | 99 % reached 27.3 mm from the corner along the diagonal | | | |

- Floor and plate BLs are almost identical (δ99 ≈ 26 mm). H ≈ 1.65 is above the equilibrium flat-plate value (≈ 1.3–1.4),
  so the BL is still recovering from the separation at the blunt 10 mm leading edge. This also explains why δ99 ≈ 26 mm
  is much more than the flat-plate estimate (≈ 6 mm). The 1/7 law fits only the outer part.
- At 10 mm from the wall, u = 28.4 m/s near the corner vs 26.0–26.7 m/s far from it (+6–9 %). Below about 13 mm the
  near-corner profiles are fuller (more momentum near the wall). Above that they stay below the edge velocity because
  they run inside the other wall's BL.
- Bisector: 99 % edge velocity at 27 mm from the corner vs √2·δ99 ≈ 36 mm for two simply overlapping BLs → fast fluid
  reaches about 25 % closer into the corner than simple superposition predicts. This is evidence of corner secondary flow
  carrying high-momentum fluid along the diagonal (confirm in Step D).

### Step B: vorticity on plane_z0 (z = 0) and first secondary-flow vectors
- Plane range: ω_x −1.89e5 / +2.06e5, ω_y −1.91e5 / +1.85e5, ω_z −1.9e4 / +2.0e4 s⁻¹ (wall values; u_τ²/ν ≈ 1.5e5 ✓).
  Plot ranges used: ω_x, ω_y ±3000; ω_z ±300 (±1000 too coarse).
- ω_y: + (red) on the inner plate face, − (blue) on the outer face, as predicted (ω_y ≈ −∂w/∂x with flow in −z). The band is
  strongest a few cm above the floor and fades into the corner: the vortex lines bend from the plate (ω_y) toward the floor (ω_x).
- ω_z full plane: the strongest streamwise vorticity is in equal and opposite pairs at the FREE EDGES (plate tip, floor tip)
  and around the OUTSIDE convex corner (≥ ±300). Inside (junction) corner: weak pair, ≈ +100 s⁻¹ along the plate and
  ≈ −100 s⁻¹ about 1–3 cm above the floor → a counter-rotating corner pair from vortex-line tilting (∇·ω = 0).
- In-plane vectors (In Plane, Z component off, scale 60, about 3 × 3 cm zoom):
  - Outside corner: strong cross-flow wrapping around the convex corner.
  - Along both walls away from the corner: small outward arrows = displacement of the growing BLs (~0.5 m/s).
  - **Inside corner:** a circulation cell on the floor side of the corner. Fluid descends toward the floor about 2–4 cm from
    the plate, moves along the floor TOWARD the plate, and rises up along the plate face close to it. This is consistent
    with the ω_z < 0 patch above the floor.
  - Effect on momentum: the downwash brings high-momentum fluid toward the floor 2–4 cm from the plate, which explains
    Step A (fuller near-corner profiles; bisector reaches the edge velocity at 27 mm instead of ~36 mm). The upwash along the
    plate lifts low-momentum fluid off the corner.
  - Likely origin: the junction stagnation at the inside corner of the blunt front face (Stage 1 iso_p819 blob), which
    rolls into a streamwise vortex (leg) that trails downstream. Check with planes at z = +0.2 (near the LE) and z = −0.2.
  - Standard SST cannot produce stress-induced corner secondary flow (Prandtl's 2nd kind) → Stage 4 (corner flow
    correction / RSM) is the natural test.

### Step B/C/D cross-plane pictures (saved in C:\Users\am1230752\BTP_images, 2–3 per plane; choose for the report later)
Planes: plane_zp20 (z = +0.2), plane_zp10 (+0.1), plane_z0 (0), plane_zm20 (−0.2). ω_z ±300, vectors In Plane, Z component off,
scale 30 (plus z0 at scale 60). Saved view `corner_zoom` (about 3 × 3 cm at the inside corner).
- z = +0.2: inside the LE separation bubble → strong (saturated) streaky ω_z on all walls; in-plane flow is a strong outward
  displacement away from the L (≥ 2× the z = 0 level) that hides the corner vortex. Corner: + patch in the corner, − band up the plate.
- z = 0: weak corner pair (±100 s⁻¹), circulation cell on the floor side (down 2–4 cm from the plate, toward the plate along
  the floor, up along the plate).
- z = −0.2: the inside-corner vortex has nearly vanished; the free-edge (floor tip) pair persists → the junction vortex decays
  downstream as the thickening turbulent BLs diffuse it.

### Stage 3 figures from data (`stage3_figures.py`, data `data/stage3/fine_planes_wall.zip` = fine_planes.csv + fine_wall.csv)
Figures: `figures/stepB_wz_planes.png`, `figures/stepB_wx_wy_z0.png`, `figures/stepD_isovels_vectors.png`, `figures/stepE_cf.png`.

Corner-vortex strength (window 0–60 mm from both walls, excluding the 2 mm near-wall skew layer):

| z (m) | Γ+ (×10⁻³ m²/s) | Γ− (×10⁻³ m²/s) | max abs(ω_z) (1/s) | max cross-flow (m/s) |
|---|---|---|---|---|
| +0.20 | 160 | −145 | 1680 | 3.5 |
| +0.10 | 53 | −29 | 293 | 0.60 |
| 0 | 29 | −19 | 123 | 0.35 |
| −0.20 | 18 | −14 | 51 | 0.59 |

→ The corner circulation decays by about 9× from just behind the LE to just before the TE.

Secondary-flow direction (numbers from the interpolated planes):
- z = +0.1 and 0: within 3 mm of each wall the cross-flow points TOWARD the corner (floor: vx ≈ −0.1 to −0.33 m/s; plate:
  vy ≈ −0.2 to −0.46 m/s). Along the bisector it points OUT of the corner (+0.07 to +0.28 m/s at 10–40 mm).
  → A symmetric pair of counter-rotating streamwise vortices: + (anticlockwise looking downstream) on the plate side,
  − (clockwise) on the floor side. The floor-side cell has the sense of a horseshoe-vortex leg (toward the body along
  the floor, up along the body).
- z = −0.2: the whole cross-flow points toward the corner and walls (0.1–0.5 m/s): the flow converges toward the L near the TE.
- **Correction to Step A:** the high-momentum fluid is NOT carried in along the bisector. It is swept down onto each wall
  about 15–30 mm from the corner (the downwash side of each cell). This thins the BL there (the 99 % isovel reaches
  27 mm along the diagonal) and raises Cf. Low-momentum fluid collects in the very corner and is ejected along the bisector.

Skin friction (Cf = τw / ½ρU∞², ×10³), floor and plate inside faces:

| z | Corner, 0–4 mm | Peak (location) | Far, 140–250 mm |
|---|---|---|---|
| +0.10 | 1.1–1.3 | 2.7–3.0 at 17–19 mm | 1.6–1.8 |
| 0 | 1.9–2.0 | 2.8–3.0 at 19–48 mm | 2.2–2.4 |
| −0.20 | 2.1 | 3.3 at 22–38 mm | 2.9 |

- The corner itself has 30–55 % LOWER Cf than the far field (slow fluid collected there). About 15–30 mm from the corner,
  Cf is 15–50 % HIGHER than far (the downwash of the corner vortices).
- Floor map: reversed wall shear (LE separation bubble) from the LE (z = 0.23) to about z = 0.16 → reattachment about
  70 mm (≈ 7 plate thicknesses) behind the blunt LE. The bubble is shorter close to the corner. Cf rises downstream as
  the BL recovers.
- Conclusion: the junction flow is a skew-induced (Prandtl's first kind) corner-vortex pair that originates at the blunt
  leading-edge junction (stagnation and separation) and decays downstream. SST cannot produce stress-induced (second
  kind) corner flow → Stage 4 test.

### Convergence histories (`convergence_plots.py`, data `data/convergence/`, figure `figures/convergence_monitors.png`)
- The fine-mesh reference values were corrected at iteration **178** (not ~162 as estimated earlier). cd before that is
  rescaled by 1/(36² × 0.1472) = 1/190.77; this gives a continuous history.
- Exact means over the last 200 iterations (± half-range):

| Mesh | cd | v_corner (m/s) | v_wake (m/s) |
|---|---|---|---|
| Coarse | 0.063731 ± 0.05 % | 33.195 ± 0.60 % | 28.569 ± 0.38 % |
| Medium | 0.062529 ± 0.03 % | 29.546 ± 0.07 % | 27.162 ± 0.04 % |
| Fine | 0.061649 ± 0.05 % | 28.304 ± 0.90 % | 25.600 ± 0.43 % |

- GCI rerun with these means (`gci.py`): cd monotonic, p = 1.25, φ_ext = 0.0594, e_a21 = 1.43 %, **GCI_fine = 4.6 %**;
  v_corner monotonic, p = 4.2, φ_ext = 27.69, e_a21 = 4.39 %, **GCI_fine = 2.7 %**; v_wake R = 1.11 (no asymptotic
  convergence), e_a21 = 6.1 %. These replace the earlier GCI table values.
- Observation: the medium mesh is the steadiest. The fine and coarse meshes show small bounded oscillations at the corner
  points (0.4–0.9 %).

## 9. Decision: Stage 4 skipped
Stage 4 (SST corner-flow correction / RSM) was skipped by the student's choice (time). Justification for the report and viva:
- SST k-ω is the standard RANS model for wall-bounded flows with separation; y⁺ < 1 resolves the sublayer. It captures the
  dominant physics here: BL growth, LE separation and reattachment (~70 mm), the skew-induced (Prandtl first-kind)
  corner-vortex pair generated at the blunt-LE junction, and its effect on Cf.
- Known limitation: an isotropic eddy-viscosity model cannot produce stress-induced (second-kind) secondary flow, which is
  typically ~1–3 % of the main velocity. Our cross-flow is ~10 % of U∞ near the LE (first kind dominates) and ~1 % at
  mid-length and downstream → the downstream corner details carry model uncertainty.
- Numerical uncertainty (GCI: cd 4.6 %, v_corner 2.7 %) and modelling uncertainty are separate; state both.
- Future work: SST corner-flow correction (one checkbox, restart from the fine solution) or Stress-BSL RSM; Step C pathlines
  and Step E wake lines (also skipped).

### Cf, refined comparison (reference band 60–150 mm from the corner wall; corner = 0–4 mm; downwash band = 15–30 mm)
| z | floor: corner / band / far (×10³) | plate: corner / band / far |
|---|---|---|
| +0.1 | 1.05 (−51 %) / 2.86 (+32 %) / 2.16 | 1.19 (−45 %) / 2.44 (+13 %) / 2.16 |
| 0 | ≈1.9 (binned) / 2.92 (+12 %) / 2.60 | ≈2.0 / 2.65 (0 %) / 2.66 |
| −0.2 | 2.06 (−33 %) / 3.29 (+8 %) / 3.06 | 2.14 (−31 %) / 3.14 (+2 %) / 3.09 |
→ Corner Cf is 30–50 % lower; the downwash band is up to +30 % higher near the front, and this fades downstream. **This supersedes the earlier "−30 to −55 % / +15 to +50 %" numbers.**
Separation bubble on the floor (reversed wall shear): reattachment 40–50 mm behind the LE within 30 mm of the plate, vs
70–77 mm far from it → the bubble is shorter near the junction.

## 10. Status at end of session (18-11-2026)
- Chat session: https://claude.ai/code/session_01LBX8cFrBzMiXoZ8KVkkDWW (can be opened from any device on the same account).
- In the repo: all uploaded data (`data/`), analysis scripts (`*.py`), figures (`figures/`), the report (`report/`,
  including `BTP_final_report_overleaf.zip`), and all 110 screenshots shared in the chat (`chat_screenshots/`,
  numbered in chat order: 1–20 geometry/meshing, ~21–60 setup and fine run, ~61–80 medium/coarse, ~81–107 Stage 3 Fluent
  plots, 108 LE iso-surface, 110 first Overleaf render).
- NOT in the repo: the Ansys project (`bbttpp_14.wbpj` + `bbttpp_14_files`, several GB). The plan is to archive it
  (Workbench File → Archive → .wbpz incl. results) and put it on Google Drive. **Add the Drive link here.**
- Fluent pictures (local, college computer): C:\Users\am1230752\BTP_images\ → copy them to Drive as well.
- Report: main body = 10 pages (checked with the stand-in class). To do: compile with the real iitdamthes.cls on Overleaf
  and check the length; fill in "Contribution of Authors"; check the AI disclosure; further edits as needed; extended
  abstract (format not yet known).
- Skipped (future work): Step C pathlines, Step E wake lines, Stage 4 (SST-CFC/RSM).
- To resume in a new session: "Read BTP_project_log.md and report/report.tex on branch claude/brave-turing-2k4h23 first."
