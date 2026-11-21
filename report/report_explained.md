# The final report, explained section by section

This is a study guide for the viva. It walks through `report.tex` in the order of the report. For every part it says
**what the report says**, **what that means**, **where the number comes from**, and **what you could be asked**.
At the end there is a one-page list of key numbers and a set of likely viva questions with answers.

Coordinates used everywhere (the same as in Fluent):

| Symbol | Direction | Velocity component |
|---|---|---|
| x | normal to the vertical plate (across the floor) | u |
| y | normal to the floor (upward, along the plate) | v |
| z | along the plates; the **flow goes in −z** | w (negative in the main flow) |

The inside corner of the L is the line x = y = 10 mm. The leading edge (LE) is at z = +0.23 m, the trailing edge
(TE) at z = −0.23 m, and the mid-length is z = 0.

---

## 0. Front matter

### Title page, declaration, certificate
These come from the department template (`iitdamthes.cls`). The title is kept from the mid-semester report,
so the committee sees it is the same project. `\endsem` replaces `\midsem`.

### Acknowledgements and the AI disclosure
The template's declaration says that any use of AI must be disclosed in the Acknowledgements. The paragraph says
exactly what the AI was used for: guiding the Fluent setup, writing the Python post-processing scripts, suggesting
interpretations, and drafting text. It also says what **you** did: you ran every simulation, every number comes
from your data, and you checked the analysis. Read it and change anything that is not accurate. You are signing
the declaration, so it must match what actually happened.

### Contribution of Authors
Still a placeholder. You and Ankit must write who did what in this phase.

### Abstract
A one-paragraph summary of the whole report: problem → method → verification → main physical results →
limitation. It contains the headline numbers (GCI 4.6 % and 2.7 %, C_d = 0.0617, separation 40–77 mm, C_f
30–50 % lower in the corner, 9× decay of the vortices). If you remember the abstract, you remember the report.

### Notation
Every symbol used in the report. Three that are less common:
- **H = δ\*/θ (shape factor):** tells you how "full" a boundary-layer profile is. About 1.3–1.4 for a healthy
  turbulent layer, larger for a layer that has been through separation or an adverse pressure gradient.
- **Γ± (circulation):** the total strength of the positive and negative streamwise vorticity in the corner,
  Γ = ∫ω_z dA. Units m²/s.
- **h = (V/N)^(1/3):** the "average cell size" used by the GCI method. V is the fluid volume (0.597 m³) and N the
  number of cells.

---

## Chapter 1. Introduction and Literature Review

### Paragraph 1: what a junction flow is
Wherever a body meets a wall (wing–fuselage, fin–hull, bridge pier–river bed), the boundary layer of the wall and
the boundary layer of the body meet in a corner. Even if the oncoming flow is simple, the corner flow becomes
three-dimensional:
- a vortex forms at the leading edge of the junction,
- the fluid moves sideways (cross-stream) along the corner, which is called **secondary flow**,
- the wall shear (and so the drag, heat transfer, scour) in the corner differs from that on each surface alone.

Reference: Simpson (2001), the standard review of junction flows. Nakayama & Rahai (1984) is the experiment the
project started from: a plate standing normal to a wall, with measurements of velocities, Reynolds stresses and
skin friction behind it.

### Paragraph 2: the theory we use to explain the results
**Two kinds of secondary flow** (Bradshaw 1987). You must know this distinction well.

| | First kind ("skew-induced") | Second kind ("stress-induced") |
|---|---|---|
| Cause | existing vorticity is **tilted/skewed** by the mean flow (pressure gradient, change of geometry) | the turbulent normal stresses are **not equal** (anisotropy) in a straight corner |
| Strength | strong, up to tens of % of the main velocity | weak, about 1–3 % |
| Example | horseshoe vortex at a wing–body junction | flow in a long square duct |
| Can SST predict it? | **yes** (any RANS model) | **no** (needs a model with unequal normal stresses) |

**∇·ω = 0 (vorticity is solenoidal).** Vorticity is the curl of velocity, and the divergence of a curl is always
zero. So vortex lines behave like magnetic field lines: they cannot start or end inside the fluid. They must close on
themselves or end on a boundary.

Why that matters here:
- The floor boundary layer has vortex lines lying **flat on the floor, pointing across the flow** (along x): ω_x.
- The plate boundary layer has vortex lines lying **flat on the plate, pointing across the flow** (along y): ω_y.
- At the corner they meet. A vortex line coming along the floor cannot stop at the corner, so it must **turn the
  corner and continue up the plate**. Where it turns, part of it gets **tilted into the flow direction** (z). That
  tilted part is streamwise vorticity ω_z, and streamwise vorticity is a swirl in the cross-plane, i.e. a corner vortex.

**SST k–ω** (Menter 1994) is the standard model for wall-bounded flows with separation. Its limitation (Pope 2000):
it uses one isotropic eddy viscosity, so it cannot create the second kind of secondary flow.

### Paragraph 3: objectives
1. A **corrected and verified** simulation, with a three-grid uncertainty estimate (Celik et al. 2008).
2. An **explanation** of how the two boundary layers meet in the corner, using vorticity and ∇·ω = 0.
3. A **quantitative comparison** of the corner with places far from it.

These three objectives are exactly what Chapter 3 delivers, in that order: verification (3.1), physics (3.2–3.6),
comparisons near vs far (all the way through).

---

## Chapter 2. Formulation and Methodology

### 2.1 Geometry, model and mesh (Figure 2.1, Table 2.1)

**Geometry.** Two plates, each 460 mm long (L), 320 mm wide and 10 mm thick, joined in an L. Square (blunt) edges.
The box around them is 200 cm long, 60 cm wide, 50 cm high, with 77 cm of free stream before and after the L.

**Reynolds number.** Re_L = U∞ L / ν = 36 × 0.46 / 1.46×10⁻⁵ = **1.13×10⁶**, so the boundary layers are turbulent.

**Boundary conditions** (Table 2.1, right column):
- Inlet: 36 m/s, turbulence intensity 1 %, viscosity ratio 10 (a clean wind-tunnel-like stream).
- Outlet: 0 Pa gauge; backflow turbulence 5 % and 10 (sensible values in case some flow re-enters).
- **The four side faces are symmetry planes.** This means zero normal velocity and zero shear, so the L sits in
  "open air". In the mid-semester run they were no-slip walls, which turned the domain into a duct: the walls grew
  their own boundary layers, the core flow sped up to 41.8 m/s and the stagnation pressure came out at 476 Pa instead
  of ½ρU² = 794 Pa.
- The L itself is a no-slip wall.

**Mesh.**
- Tetrahedral cells in the volume, plus **25 prism (inflation) layers** on every face of the L. First layer
  0.01 mm, growth 1.2 → the stack is about 4.7 mm thick.
- Why 0.01 mm: we wanted y⁺ ≈ 1, so that SST resolves the viscous sublayer instead of using wall functions.
  Estimate: C_f ≈ 0.003 → u_τ = U√(C_f/2) ≈ 1.4 m/s → y = y⁺ν/u_τ ≈ 0.01 mm. The result (y⁺ max 0.77–0.93) confirms it.
- A **body of influence (BOI)** is a box around the L where the cells are forced to be small. It is not a physical
  object; it only controls the mesh size.
- **Three grids** were made by changing only two settings, the face size on the L and the BOI size, by a factor of
  about 1.45 each time. Inflation, domain, BCs and solver were identical.

**Solver** (Table 2.1): pressure-based, steady, **coupled** pressure–velocity solver with pseudo-transient
relaxation, second-order schemes for everything. The mid-semester run used SIMPLE with very low relaxation
(0.1/0.2), which converges slowly. The coupled solver solves pressure and momentum together and converged in a few
hundred iterations.

### 2.2 Analysis

**Equation (2.1), the streamwise vorticity equation.** It says how ω_z (the corner swirl) changes as the fluid
moves downstream:

  u·∇ω_z = ω_x ∂w/∂x + ω_y ∂w/∂y  (tilting)  + ω_z ∂w/∂z (stretching) + diffusion

- **Tilting:** existing cross-stream vorticity (ω_x of the floor, ω_y of the plate) is turned into ω_z when the
  streamwise velocity w changes across it. ∂w/∂x is large only near the plate and ∂w/∂y only near the floor, so
  **both terms are active only in the corner**. That is why the corner, and not the open wall, makes streamwise vortices.
- **Stretching:** an existing vortex is strengthened if the flow stretches it along its axis.
- **Diffusion:** viscosity and turbulence spread vorticity out and weaken it. This is what makes the vortices decay
  downstream.

The second relation, ∂ω_z/∂z = −(∂ω_x/∂x + ∂ω_y/∂y), is ∇·ω = 0 written out. It says: wherever ω_x and ω_y change
across the cross-section (as they do in the corner, where the floor's vortex lines turn into the plate's), ω_z
**must** change along the flow. That is the kinematic reason a corner vortex has to appear.

**What was measured, and how:**
- **Profiles** at mid-length (z = 0): normal to each wall at 240 mm ("far", a plain boundary layer) and at 10 mm
  ("near", in the corner) from the other wall, plus along the 45° bisector out of the corner. Exported from Fluent
  as XY plots.
- **Four cross-planes** at z = +0.20, +0.10, 0, −0.20 m (30, 130, 230 and 430 mm behind the LE): velocity,
  vorticity, pressure and k exported as CSV. **Wall data** on the L: wall shear, C_f, y⁺. All analysed in Python
  (`stage3_figures.py`, `stepA_profiles.py`).
- **Circulation Γ±:** the CSV points were interpolated onto a regular 0.25 mm grid in a 60 × 60 mm window at the
  corner, and ω_z was summed separately where it is positive and where it is negative. The first 2 mm next to each
  wall are excluded, because there is a very thin, very strong near-wall layer of ω_z (slight sideways skew of the
  wall flow) that would swamp the vortices.

---

## Chapter 3. Results and Discussion

### 3.1 Verification (Table 3.1)

**What "converged" means here.** Each case ran 500 iterations. Over the last 200:
- C_d changed by less than 0.05 %, the two corner velocities by less than 0.9 % (these are small, bounded
  oscillations, not a drift);
- the mass imbalance between inlet and outlet was below 2×10⁻⁴ %;
- residuals were flat (they plateau; with the coupled solver the monitors matter more than the residual level).

**Monitor points.** v_corner at (0.02, 0.02, 0) m: 10 mm from both walls at mid-length. v_wake at (0.02, 0.02, −0.35) m:
10 mm from both walls, 12 cm behind the TE, in the corner wake.

**The grid study (GCI, Celik et al. 2008).** Read Table 3.1 as follows:

| Row | Meaning |
|---|---|
| N, h | cells and average cell size. Ratio between grids r = h_coarse/h_medium = h_medium/h_fine = 1.30 (Celik recommends r > 1.3) |
| C_d, v_corner, v_wake | the three monitored values, averaged over the last 200 iterations |
| Apparent order p | how fast the solution converges with h. Calculated from the three values. For a second-order scheme you expect p ≈ 2 |
| Extrapolated value | Richardson extrapolation: the estimate of the value on an infinitely fine mesh |
| GCI_fine | error band on the fine-mesh value: GCI = 1.25 × (relative change medium→fine) / (r^p − 1). The 1.25 is a safety factor |

How to read the results:
- **C_d:** 0.06373 → 0.06253 → 0.06165. The changes shrink (monotonic convergence). Medium→fine change 1.4 %, below
  the 2 % the professor asked for. GCI 4.6 % → **C_d = 0.0617 ± 0.0028**. p = 1.25 is lower than 2, which is common
  with tetrahedral meshes and sharp edges.
- **v_corner:** 33.20 → 29.55 → 28.30 m/s, also monotonic. GCI 2.7 % → **28.3 ± 0.8 m/s**. p = 4.2 is higher than
  the formal order; Celik warns that GCI is then less reliable, so treat it as an estimate.
- **v_wake:** 28.57 → 27.16 → 25.60 m/s. The second change is larger than the first (ratio R = 1.11 > 1), so it is
  not converging monotonically and GCI is not defined. We report the spread (about 6 %). Reason: the point is near
  the downstream end of the BOI, where cells grow quickly, and it sits in the wake where gradients are strong. It
  is the most mesh-sensitive quantity, and the report says so honestly.

**Why the fine mesh is used afterwards:** it is the most accurate, and the corner needs it (v_corner still changes
4.4 % from medium to fine).

**One extra detail you should know:** on the fine run, the reference values (area 0.1472 m², length 0.46 m,
velocity 36 m/s) were corrected at iteration 178. Before that, Fluent used its defaults (1 m², 1 m/s), so C_d printed
as 11.76. This only changes how C_d is normalised, not the flow. The convergence plot rescales those first 177
values (divide by 36² × 0.1472 = 190.8).

### 3.2 Leading edge of the junction

**Pressure check.** Inlet total pressure = 25 Pa static + 794 Pa dynamic (½ × 1.225 × 36²) = 819 Pa. The inlet static
pressure is 25 Pa, not 0, because the outlet is the 0 Pa reference and the flow needs a small pressure difference to
push past the L.

**Peak pressure on the L: 837 Pa (on nodes).** In principle nothing can exceed the upstream total pressure, so the
2 % excess is a numerical overshoot at the sharp stagnation edge (normal for a second-order scheme at a corner).
Single cells showed even larger spikes (869 Pa, 66 m/s). They are not physical and do not affect the integrated values.

**Where the stagnation is strongest.** Iso-surfaces of 819 Pa (Fluent picture) showed the largest high-pressure
region at the **inside corner of the blunt front face**. Fluid approaching that corner is blocked by **both** plates
at once, so it slows down more than at a single face. This is where the junction flow starts.

**Edge acceleration and separation.** The flow speeds up around the sharp 10 mm square edges (up to 1.24 U∞ on nodes)
and separates, forming a bubble on every face. On the floor, the wall shear points backwards (reversed flow) from
the LE to:
- 70–77 mm downstream far from the plate,
- only 40–50 mm downstream within 30 mm of the plate.

So **the bubble is shorter in the junction.** This comes from the wall data (reversed z-wall-shear), visible as the
orange dots in Figure 3.4(a).

### 3.3 Boundary layers far from and near the junction (Figure 3.1)

**Far from the junction** (blue curves): a normal turbulent boundary layer on each wall, almost identical on floor
and plate.
- δ₉₉ = 25.6 mm (floor) and 26.0 mm (plate): the height where u reaches 99 % of the edge velocity.
- δ\* ≈ 6.2 mm (displacement thickness), θ ≈ 3.8 mm (momentum thickness), H ≈ 1.65.
- **Why so thick?** A flat plate with a sharp, smooth leading edge would have δ ≈ 0.37 x Re_x^(−1/5) ≈ 6 mm at
  x = 230 mm. Ours is four times thicker because the layer started with a **separation bubble** at the blunt LE; it
  reattaches thick and turbulent. H ≈ 1.65 (above the equilibrium 1.3–1.4) says the same thing: the layer is still
  recovering.
- The edge velocity is 37.4 m/s, 4 % above U∞, because the L displaces the flow around it.
- The dashed 1/7-power-law curve is the textbook turbulent profile with the same δ₉₉. Our profiles are less full
  near the wall, which is again the signature of a recovering layer.

**Near the junction** (orange curves, 10 mm from the other wall):
- Close to the wall they are **fuller**: at 10 mm from the wall, 28.4 m/s near the corner vs 26.0–26.7 m/s far
  away (+6–9 %).
- Further out they **never reach the edge velocity** (they flatten out at about 33–35 m/s). That is simply because
  these lines run 10 mm from the other wall, so they stay inside the other wall's boundary layer all the way up.
  This is the overlap of the two boundary layers.

**Along the bisector** (panel c): 99 % of the edge velocity is reached 27 mm from the corner. If the two boundary
layers were just superposed with no interaction, a point on the bisector at distance s is s/√2 from each wall, so
it would need s/√2 ≥ δ₉₉, i.e. s ≥ √2 × 26 ≈ 36 mm. 27 < 36 means **fast fluid reaches closer to the corner than
superposition allows**. Something is moving momentum around in the corner: a secondary flow. The next two sections
show what it is.

### 3.4 Vorticity at the corner (Figure 3.2)

**Signs of the wall vorticity.** The flow is in −z. On the floor, |w| grows upward, so ω_x ≈ ∂w/∂y < 0. On the plate,
|w| grows in +x, so ω_y ≈ −∂w/∂x > 0. Both are about 2×10⁵ s⁻¹ at the wall, which matches the estimate u_τ²/ν.

**What happens at the corner.** On the z = 0 plane (Fluent contours, and the ω_x/ω_y figure in the repo) the floor's
ω_x layer thins near the plate and the plate's ω_y layer weakens near the floor. The floor's vortex lines are turning
into the plate's. Where that happens, ∂ω_x/∂x + ∂ω_y/∂y ≠ 0, so by equation (2.1) ω_z must change along the corner.

**Figure 3.2, read panel by panel:**
- z = +0.20 m (30 mm behind the LE, inside the separation bubble): strong, patchy ω_z on both walls. The bubble is
  three-dimensional and churns up streamwise vorticity everywhere; the corner pair cannot be separated from it yet.
- z = +0.10, 0, −0.20 m: a clean, almost mirror-symmetric **pair**: positive ω_z (red) along the plate, negative
  (blue) above the floor, centred 5–20 mm from the walls.
- The thin red line right along the floor is the very-near-wall layer (excluded from Γ).

**Circulation.** Γ+/Γ− (×10⁻³ m²/s): 160/−145 → 53/−29 → 29/−19 → 18/−14. That is a **nine-fold decay** from the LE
to the TE. The vortices are strongest near the LE and weaken downstream because turbulent diffusion in the growing
boundary layers spreads and cancels the vorticity, and there is no strong tilting further downstream to replenish it.

**Conclusion of the section:** the corner vortices are **created near the leading edge**, where stagnation and
separation tilt the wall vorticity most strongly. Created by tilting = **secondary flow of the first kind**.

### 3.5 Secondary flow and mixing in the corner (Figure 3.3)

**How to read Figure 3.3:** colour = speed |u|; black lines = isovels (lines of constant speed, labelled in m/s);
orange arrows = the cross-flow (u, v), i.e. the motion in the plane perpendicular to the main flow. The arrows are
small (tenths of m/s), so they are drawn on a magnified scale (reference arrow on top of each panel).

**Direction of the circulation** (read from the interpolated data, not only from the picture):
- within 3 mm of each wall, the cross-flow points **toward the corner** (0.1–0.46 m/s);
- along the bisector it points **out of the corner** (0.07–0.28 m/s).

So each vortex works like a conveyor belt:
1. it drags **slow** near-wall fluid along its wall **into** the corner,
2. pushes it **out** of the corner along the bisector,
3. and on its outer side brings **fast** outer fluid **down onto the wall**, about 15–30 mm from the corner.

The floor-side vortex rotates in the same sense as a horseshoe-vortex leg (toward the body along the floor, up along
the body).

**Link back to Section 3.3:** the fast fluid brought down beside the corner makes the near-wall profiles fuller there
and squeezes the isovels toward the walls, which is why the bisector reaches the edge speed already at 27 mm.

**The two end stations:**
- z = +0.20: cross-flow about 10× stronger (3.5 m/s) and pointing **away** from the L everywhere. The blunt nose and
  the bubble push the flow outward. (This panel uses a reference arrow about 7× larger.)
- z = −0.20: the cross-flow converges toward the walls as the flow approaches the trailing edge.

**Correction you should know about:** in the middle of the work we first thought fast fluid was carried *into* the
corner along the bisector. The exported data showed the opposite direction along the bisector (outward). The final
report uses the data. If someone remembers the earlier version, this is the explanation.

### 3.6 Wall shear stress (Figure 3.4)

**C_f = τ_w / (½ρU∞²)**, the wall shear made dimensionless with the inlet dynamic pressure.

**(a) The floor map.** C_f over the whole inside face of the floor. Orange dots = reversed wall shear (separation
bubble). It ends earlier near the plate (bottom edge of the map) than far from it. Downstream, C_f rises as the
boundary layer recovers.

**(b) C_f across the span** at three stations, plotted against distance from the other wall (log scale, so the
corner region is stretched out). Solid = floor, dashed = plate. The numbers:

| Station | In the corner (0–4 mm) | 15–30 mm from the corner | Far (60–150 mm) |
|---|---|---|---|
| z = +0.10 floor | 1.05×10⁻³ (−51 %) | 2.86×10⁻³ (+32 %) | 2.16×10⁻³ |
| z = −0.20 floor | 2.06×10⁻³ (−33 %) | 3.29×10⁻³ (+8 %) | 3.06×10⁻³ |

- **Lower in the corner (−30 to −50 %):** slow fluid is collected there by the vortices; slow fluid near the wall
  means a small velocity gradient and so low shear.
- **Higher just beside it (up to +32 %):** that is where the vortices bring fast fluid down onto the wall; steeper
  gradient, higher shear.
- **The excess fades downstream** (+32 % → +8 %) together with the vortex strength (Γ falls nine-fold). Two
  independent data sets (vorticity and wall shear) tell the same story.

### Relation to the reference experiment (paragraph at the end of Chapter 3)

Nakayama & Rahai had a plate standing on a long wall, with a **thick turbulent boundary layer arriving from upstream**.
That incoming layer separates in front of the plate and rolls into a strong horseshoe vortex. In our L both boundary
layers **start at the same blunt leading edge**, so there is no incoming layer to roll up; our corner vortices are
generated by the LE stagnation and separation instead. That is why the comparison is **qualitative**: both flows show
streamwise corner vortices, momentum redistribution and a local change in wall shear, but the numbers cannot be
compared one-to-one.

---

## Chapter 4. Conclusions and Future Work

The four conclusions are the four results above, compressed:
1. **Verification:** y⁺ < 1, three grids, r = 1.3 → C_d = 0.0617 ± 4.6 %, corner velocity converged to 2.7 %.
2. **Leading edge:** stagnation strongest at the inside corner; separation bubble shorter near the junction
   (40–50 mm) than far from it (70–77 mm).
3. **Vorticity:** ∇·ω = 0 forces the floor and plate vortex lines to join through the corner; tilting there makes a
   symmetric counter-rotating pair of streamwise vortices, decaying nine-fold from LE to TE.
4. **Secondary flow and wall shear:** slow fluid into the corner and out along the bisector, fast fluid onto the walls
   15–30 mm away; C_f 30–50 % lower in the corner and up to 32 % higher beside it.

**Limitations and future work:**
- SST cannot produce the second kind of secondary flow (1–3 % of U∞). Near the LE our cross-flow is about 10 % of U∞,
  so the first kind dominates and SST is adequate there. Downstream the cross-flow is about 1 %, the same size as
  second-kind effects, so details there carry model uncertainty.
- Next steps: SST with corner-flow correction or a Reynolds-stress model; a finer mesh in the corner wake (the
  v_wake point did not converge); an incoming wall boundary layer to match Nakayama & Rahai quantitatively; the
  NACA 0010 wing–body junction designed in XFLR5 in the first phase.

---

## Key numbers (memorise these)

| Quantity | Value |
|---|---|
| U∞, Re_L | 36 m/s, 1.13×10⁶ |
| ½ρU∞² | 794 Pa (inlet total pressure 819 Pa) |
| Plates | 460 × 320 × 10 mm |
| Grids | 0.53 / 1.15 / 2.53 M cells, r = 1.30 |
| y⁺ | average ≈ 0.4, max 0.77–0.93 |
| C_d | 0.0617, GCI 4.6 %, medium→fine change 1.4 % |
| v_corner | 28.3 m/s, GCI 2.7 % |
| v_wake | 25.6 m/s, about 6 % spread (not converged) |
| δ₉₉, H at mid-length | ≈ 26 mm, ≈ 1.65 (flat-plate estimate 6 mm) |
| Separation bubble | 40–50 mm near the junction, 70–77 mm far |
| Bisector | edge velocity at 27 mm vs √2 δ₉₉ ≈ 36 mm |
| Circulation Γ+ / Γ− | 160/−145 → 18/−14 ×10⁻³ m²/s (9× decay) |
| Cross-flow | 3.5 m/s at z = +0.20; 0.1–0.5 m/s further back |
| C_f in the corner | 30–50 % lower; up to +32 % at 15–30 mm |

---

## Likely viva questions, with answers

**Why did you change from a T-shape in a box to an L in open air?**
The box walls were no-slip, so the domain behaved like a duct: the flow accelerated to 41.8 m/s and the stagnation
pressure was wrong (476 Pa instead of 794 Pa). Symmetry side faces remove that blockage. The L isolates one clean
junction, which is what the professor asked us to focus on.

**Why SST k–ω, if it cannot predict corner flow of the second kind?**
SST is the standard RANS model for wall-bounded flows with separation, and with y⁺ < 1 it resolves the wall layer. It
captures the main physics here: separation and reattachment, boundary-layer growth, and the first-kind corner vortices
created at the leading edge (cross-flow ≈ 10 % of U∞). The second kind is about 1–3 %, so it matters only far
downstream, where our cross-flow is also about 1 %. We state that limitation and propose the corner-flow correction or
an RSM as the next step. Numerical uncertainty (GCI) and model uncertainty are separate, and we report both.

**Why only 500 iterations?**
The iteration count is not a convergence criterion. The monitors were flat (< 0.1 % change over 200 iterations for
C_d), the residuals had plateaued, and the mass imbalance was below 2×10⁻⁴ %. The coupled pseudo-transient solver needs
far fewer iterations than SIMPLE.

**What is the GCI and how did you compute it?**
A standard (Celik et al. 2008) error band for the mesh. Three grids with r ≈ 1.3, compute the apparent order p from the
three values, extrapolate to zero cell size, and GCI = 1.25 × relative change / (r^p − 1). The script is `gci.py`.

**Why did you change only the face and BOI sizes, not the inflation?**
To keep the wall treatment identical (y⁺ < 1 on all grids, 0.39–0.42 average), so the differences come only from the
resolution along the walls and in the flow around the L. The far-field cells hardly affect the corner.

**Why does v_wake not converge?**
It is near the downstream end of the refinement box, where cells grow, and in the wake, where gradients are strong.
The differences between meshes do not shrink (R = 1.11). We report it as about 6 % uncertain; a longer BOI would fix it.

**What does ∇·ω = 0 have to do with the corner?**
Vortex lines cannot end in the fluid. The floor's vortex lines (across the flow, along x) must connect to the plate's
(along y) through the corner. Turning them tilts part of the vorticity into the flow direction, so streamwise vorticity
must appear in the corner. Mathematically, ∂ω_z/∂z = −(∂ω_x/∂x + ∂ω_y/∂y), and the right side is non-zero only in
the corner.

**Is this a horseshoe vortex?**
Not in the classical sense: a horseshoe vortex forms when an incoming wall boundary layer separates in front of a
body, and we have no incoming layer. But the floor-side vortex rotates in the same sense as a horseshoe-vortex leg, and
both are first-kind secondary flows created at the leading edge of the junction.

**Why is C_f lower in the corner?**
The vortices sweep slow near-wall fluid into the corner. Slow fluid next to the wall means a small velocity gradient,
so less shear. Beside the corner, where fast fluid is brought down, the gradient is steeper and C_f is higher.

**Why are your boundary layers four times thicker than the flat-plate formula?**
The formula assumes a sharp leading edge and a layer growing from zero. Our edge is a blunt 10 mm square face: the flow
separates and reattaches about 50–77 mm downstream as an already-thick turbulent layer. H ≈ 1.65 confirms it is still
recovering.

**How did you get the numbers from Fluent into the plots?**
Profiles were exported as XY files; the four cross-planes and the wall as ASCII CSV (node values). Python scripts in
the repo (`stepA_profiles.py`, `stage3_figures.py`, `convergence_plots.py`, `gci.py`) compute every number and draw
every figure, so every result can be reproduced from the data in `data/`.

**What would you do with more time?**
SST corner-flow correction or RSM; a longer and finer BOI for the wake; pathlines from the leading-edge corner to show
the vortex formation in 3D; an upstream wall boundary layer to compare quantitatively with Nakayama & Rahai; and the
NACA 0010 wing–body junction.
