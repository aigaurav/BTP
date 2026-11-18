# Paste everything below this line as the first message of the new session

---

You are helping me (Gaurav Waghmare, B.Tech, Engineering & Computational Mechanics, IIT Delhi) finish my B.Tech Project (BTP) with Ankit Kumar Modi, supervisor Prof. Arjun Sharma. You are running on my friend's Windows laptop (14 cores) that has Ansys 2024 R2 with the IIT Delhi academic licence. Reply in English even if I write in Hindi.

## 1. The project
- Title: **Turbulent flow behind a flat plate mounted normal to the wall** (a wall–plate junction flow).
- Reference experiment: Nakayama, A. and Rahai, H. R. (1984), *Measurements of turbulent flow behind a flat plate mounted normal to the wall*, AIAA Journal 22(12), 1817–1819. Measured mean velocity, secondary velocities, Reynolds stresses and skin friction behind the plate.
- Solver: Ansys Fluent 2024 R2, steady RANS, SST k–ω, air (ρ = 1.225 kg/m³, μ = 1.7894e-5 kg/m·s), inlet 36 m/s.
- Future work (not for now): realistic wing–body junction from an XFLR5 aircraft model (NACA 0010).

## 2. What was done before the mid-semester (problems found)
- Model was a **T-shape** (plate on a 50 mm thick base block) floating inside a small box. Tetrahedral mesh ~10 mm, no inflation layers.
- Problems: box side/top walls were **no-slip** (duct flow, blockage → peak 41.77 m/s instead of ~36); outlet only ~0.5 plate length behind the plate; no boundary-layer resolution; stagnation pressure 476 Pa instead of ~794 Pa (½ρU²); backflow turbulence set to 1e-14; under-relaxation pressure 0.1 / momentum 0.2 (SIMPLE); only qualitative comparison with the experiment; no grid study; no physical explanation of the junction flow.

## 3. What was done after the mid-semester (current state)
- Changed to an **L-shape** model (vertical plate + horizontal wall leg; the wall is on ONE side of the plate only).
- Added an **enclosure** box and one **refinement cuboid (Body of Influence, BOI)** between model and enclosure.
- Current mesh: ~489,121 nodes, ~2,605,876 elements, tetrahedral, global default size ~88 mm (BOI finer). Not yet confirmed: inflation layers, symmetry boundaries, whether air flows under the horizontal leg.

## 4. What the professor asked for (final presentation)
1. **Grid independence:** three meshes (coarse ~0.45 M, medium ~1.0 M, fine ~2.2 M elements) from the SAME geometry, changing only element sizes (ratio ~1.3, see section 7). Show Cd / a wake velocity changes little between medium and fine (< ~2 %); add GCI (Celik et al. 2008).
2. **Explain the physics** of every contour/streamline: why and how the junction flow forms. Use boundary-layer vorticity and **∇·ω = 0** (vortex lines cannot end; on a no-slip wall they lie flat, so the wall's ω_y lines must turn into the plate's ω_z lines at the corner, and ∂ω_x/∂x = −(∂ω_y/∂y + ∂ω_z/∂z) ≠ 0 forces streamwise vorticity near the corner).
3. Plots + three-line explanations: what we see → why → mechanism.
4. **FOCUS ON THE JUNCTION (most important instruction).** Every plot and explanation must centre on the wall–plate junction (the corner of the L): how the wall boundary layer and the plate boundary layer meet and mix there, the horseshoe vortex at the junction's leading edge, the corner vortex / secondary flow along the junction, and the corner wake behind it. Concretely:
    - Zoom every cross-plane picture to the corner region (about 3–4 δ from the corner in both directions), not the whole domain.
    - Place points, lines, rakes and planes in or right next to the corner; put monitor points in the corner (e.g. 10 mm from both wall and plate).
    - For every quantity, compare "at the junction" vs "far from the junction" (e.g. wall shear and velocity profile far from the plate vs near the corner) to show what the junction changes.
    - Explain mixing at the junction: how the two boundary layers merge, how secondary flow moves high- and low-momentum fluid in the corner, and how the corner region recovers downstream.
    - Far-field or whole-domain plots only when needed for context (e.g. convergence, y⁺).

## 5. The full guide (follow it)
Step-by-step guide doc: https://claude.ai/artifact/SBDs1ibXdp269YqrCHAB3F
It contains: Part 0 setup fixes, Part 1 grid study + GCI Python script, Steps A–E, slide plan, checklist. Summary of Steps:
- **A** incoming boundary layers (δ99, 1/7 law, ω_y on wall, ω_z on plate).
- **B** ∇·ω = 0 at the corner (X/Y/Z-vorticity on cross-planes; vortex lines in CFD-Post).
- **C** horseshoe vortex (negative wall shear upstream of leading edge, recirculation vectors, pathlines from a rake, Q-criterion).
- **D** corner secondary flow (isovels bulging into corner, in-plane vectors; SST/Boussinesq misses stress-induced secondary flow → optional RSM Stress-BSL or SST Corner Flow Correction).
- **E** wake recovery and skin friction; quantitative comparison with Nakayama & Rahai (digitise with WebPlotDigitizer).

Coordinate names used in the guide: x = streamwise, y = normal to the plate (spanwise), z = normal to the wall (height). Map these to the real Fluent axes after Stage 0.

## 6. Setup rules to apply (Part 0 of the guide)
- **Enclosure boundaries (professor's instruction):** the enclosure box has 6 faces: inlet, outlet, and four faces named **front, back, up, bottom**. Set all four (front, back, up, bottom) to **symmetry** so the domain behaves like open air, not a wind tunnel. Their current type is unknown; check in Stage 0 and change them in Stage 1. Also report in Stage 0 whether the L's horizontal leg touches the bottom face or air can flow underneath it.
- Inlet velocity-inlet 36 m/s (1 %, viscosity ratio 10); outlet pressure-outlet 0 Pa (backflow 5 %, 10); wall and plate no-slip.
- Inflation on wall and plate: first layer 0.01 mm (y⁺ ≈ 1), 25 layers, growth 1.2.
- Coupled solver, pseudo-time off, second order everywhere, hybrid initialisation.
- Reference values from inlet; area = plate side area, length = plate length.
- Monitors: Cd of plate, velocity at a wake point 1 L behind trailing edge; residuals stored for all iterations; converged = monitors flat (< 0.1 % change over 200 iterations).
- Outlet should be ≥ 3 L behind the plate; horizontal leg should act as the floor (no flow underneath). **Ask me before changing geometry.**

## 7. How we work (staged, low usage)
I am on a Claude Pro plan with a weekly limit (~36 % left). So:
- Run Fluent in **command-line batch mode** (`fluent 3ddp -t12 -g -i <journal>`), NOT by clicking the GUI (screenshots are expensive).
- Every stage writes a short **text summary** (numbers) to `C:\BTP_results\stageN\summary.txt`; read that first, and look at only the 3–5 most important images.
- Start long runs in the background and check once when finished; do not poll every few minutes.
- Work only inside `C:\BTP` and `C:\BTP_results`. Ask before installing anything.

### Stage gate — MANDATORY before and after every stage
**Before starting any stage**, stop and send me this, then wait for my explicit "yes":
1. **What you will do** in this stage (short bullet list).
2. **How long it will take** (computer time) and roughly how much of my usage it needs (small / medium / large).
3. **What you will change** in the case or mesh, if anything.
4. Ask: **"Do you want to change anything before I start?"**

**After finishing any stage**, send me:
1. A short result report (key numbers, 3–5 key images at most, problems found).
2. Your recommendation for the next stage.
3. Then go back to the "Before starting" check for the next stage. Never start the next stage on your own.

### Mesh plan (overrides the 7-million-cell plan in the guide's Part 1.1)
I do not have time for very large meshes. The **finest mesh must have about 2.0–2.3 million elements** (including inflation layers). Use a constant refinement ratio r ≈ 1.3 in cell size (≈ 2.2× in cell count):

| Mesh | Target elements | How |
|---|---|---|
| Fine | ~2.2 M (2.0–2.3 M) | Adjust BOI size (start near our current BOI size; current mesh is 2.6 M without confirmed inflation) |
| Medium | ~1.0 M | BOI size × 1.3 |
| Coarse | ~0.45 M | BOI size × 1.3² ≈ 1.69 |

Notes: only the BOI (and if needed global) element size changes; geometry, inflation settings, BCs and solver stay identical. Cell counts will not scale exactly because the inflation layers and outer region stay fixed, so tune the BOI size by trial-meshing (meshing only takes minutes) until each mesh is within ~10 % of its target, and report the actual N for each. If inflation with y⁺ ≈ 1 pushes the fine mesh above 2.3 M, tell me and propose options (fewer layers, slightly larger first layer with y⁺ < 5, or a coarser outer region) before deciding. Results for Steps A–E use the **fine** mesh.

Stages:
| Stage | Content | Expected time on 14 cores (12 processes) |
|---|---|---|
| 0 | Inspect the case: zones, domain extents, mesh size/quality, current settings (no solve) | ~1 min |
| 1 | Build the fine mesh (~2.2 M) with Part 0 fixes and solve it; convergence, y⁺, peak velocity, BL profile, basic contours | ~45–60 min |
| 2 | Medium (~1.0 M) and coarse (~0.45 M) meshes; table, GCI, profile overlay | ~30–40 min |
| 3 | Steps A–E plots and data exports + explanations (on the fine mesh, no new solve) | ~30 min |
| 4 | Optional RSM comparison on the fine mesh | ~1–1.5 h |

## 8. Files on this laptop
- Project folder: `C:\BTP` (Workbench `.wbpj` + `_files` folder, mid-sem report PDF, `ansys_scripts\`).
- `ansys_scripts\stage0_inspect.jou` (GUI version) and `ansys_scripts\stage0_inspect_batch.jou` (batch version, reads `C:\BTP\case\medium.cas.h5`).
- Results go to `C:\BTP_results`.
- Fluent is usually at `%AWP_ROOT242%\fluent\ntbin\win64\fluent.exe` (= `C:\Program Files\ANSYS Inc\v242\...`).

## 9. Start now
1. Check: Fluent install path and free disk space. Find the project: I copied the complete saved Workbench project (geometry, mesh, setup, solution and results all done) into the folder I opened. Locate the `.wbpj` file and its `_files` folder, then find the latest Fluent case/data files inside `<project>_files\dp0\FFF\Fluent\` (`*.cas.h5`, `*.dat.h5`). Copy (do not move) the case to `C:\BTP\case\medium.cas.h5` for the batch journals, or point the journals to the copied file. Never modify the original project files; work on copies. If you cannot find the files, tell me exactly what to look for.
2. Run Stage 0 in batch mode with 12 processes.
3. Read `C:\BTP_results\stage0_report.txt` and tell me: zone names and types, axis directions, plate position, mesh size and quality, what in the setup must change for Stage 1.
4. Then do the "Before starting" stage-gate check for Stage 1 (what, how long, what changes, "do you want to change anything?") and wait for my yes.

Before step 2 (running Stage 0), also do the stage-gate check for Stage 0.
