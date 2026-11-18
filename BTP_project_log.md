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

| Quantity | Iteration 300 | Iteration 500 | Change % |
|---|---|---|---|
| cd | _todo_ | _todo_ | |
| v_corner | _todo_ | _todo_ | |
| v_wake | _todo_ | _todo_ | |
| Mass flow in / out | | _todo_ | |

Stage 1 checks still to do: y⁺ on model (average and maximum), maximum velocity, maximum pressure on model (~794 Pa),
mass balance.

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
