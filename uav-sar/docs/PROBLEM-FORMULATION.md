# Mathematical formulation

What optimization problem is this system actually solving? This document states
it, then states the tractable restrictions each scheme in the codebase solves,
and marks which structural feature the measurements identified as binding.

The formulation is written *after* the experiments, deliberately. Two things the
data forced into it — the endogeneity of information (§2.3) and the rendezvous
constraint (§4) — are not in the obvious "informative path planning" template
and are where this problem differs from its neighbours.

---

## 1. Primitives

| symbol | meaning |
|---|---|
| $\mathcal{A}\subset\mathbb{R}^2$ | search region |
| $\mathcal{N}=\{1..n\}$, $p_i\in\mathcal{A}$ | ground sensors at known positions |
| $v\in\mathcal{A}$ | victim position, **unknown**, prior $\pi_0$ |
| $\mathcal{M}=\{1..m\}$ | UAVs |
| $q_u:[0,T]\to\mathbb{R}^3$ | trajectory of UAV $u$, $\|\dot q_u\|\le V$, $q_u(0)=q_u(T)=b$ |
| $\mathcal{D}=\{d_1..d_K\}$ | reference dataset (chunks) |
| $F_i(t)\subseteq\mathcal{D}$ | chunks node $i$ holds at time $t$ |
| $\mathcal{G}=(\mathcal{N},\mathcal{E})$ | ground connectivity graph, $(i,j)\in\mathcal{E}$ iff $\|p_i-p_j\|\le R_{g}$ |

**Energy.** $E=\sum_u\int_0^T P(\|\dot q_u(t)\|)\,dt$, with $P$ the rotary-wing
power curve (Zeng–Zhang): blade-profile + induced + parasitic.

**Link.** A transmission from $q$ to $p$ succeeds w.p.
$\rho(q,p)=\Pr[\text{SNR}\ge\gamma]$, determined by the A2G model — elevation-angle
LoS probability, ITU-R P.833 foliage, Nakagami fading, log-normal shadowing.
Write $R_{a}$ for the range at which $\rho$ is usable. Empirically
$R_g\approx 37$ m $\ll R_a\approx 60$–$80$ m; **this asymmetry matters** (§4).

---

## 2. State and dynamics

### 2.1 Detector

Node $i$ has a raw detector response driven by proximity to the victim,
$\kappa_i=g(\|p_i-v\|)+\varepsilon_i$, $\varepsilon_i\sim\mathcal{N}(0,\sigma_s^2)$
drawn **once per node** (it is one observation of that node's own footage, not a
per-packet event). It self-reports position $\tilde p_i=p_i+\eta_i$,
$\eta_i\sim\mathcal{N}(0,\sigma_{\text{gps}}^2 I)$, also frozen.

### 2.2 Evidence

$$e_i(t)\;=\;C\big(F_i(t)\big)\cdot\kappa_i,\qquad C(F)=1-\!\!\prod_{d\in F}\!\big(1-w_d\big)$$

with $w_d$ the utility of chunk $d$ (noisy-OR accumulation).

### 2.3 The information is endogenous — this is the crux

$F_i(t)$ grows only when a UAV is close enough to deliver chunks:

$$\Pr\big[d\in F_i(t+dt)\,\big|\,d\notin F_i(t)\big]\;=\;\rho\big(q_u(t),p_i\big)\cdot x_{u,d}(t)\,dt$$

where $x_{u,d}(t)\in\{0,1\}$ is the transmit schedule. Therefore

$$e_i(t)\ \text{is a functional of}\ \{q_u,x_u\}_{u\in\mathcal{M}}.$$

**The controller must spend airtime to create the very information it then
harvests.** This is *not* standard informative path planning, where a latent
field exists and flying merely samples it. Here $\kappa_i$ exists but is
*unusable* until $C(F_i)$ is large enough — the node cannot score its own footage
without the reference. Consequence: the value of exploring a region is zero until
that region has been cued, so exploration and exploitation are not separable in
the usual way.

### 2.4 Observability

The decision maker (an elected leader, or a UAV) knows only what physically
arrived. Define the observation available to decision point $c$ at time $t$:

$$\mathcal{I}_c(t)=\Big\{\big(i,e_i(s),\tilde p_i\big)\;:\;\exists\ \text{a successful path } i\rightsquigarrow c \text{ by } t\Big\}$$

The two schemes differ **only** in what paths exist:

- **cooperative:** multi-hop over $\mathcal{G}$ to a cell leader, then a flood
  across leaders. Reachability is a graph property — time-decoupled from UAVs.
- **closed-loop:** a single hop $i\to u$, feasible only if
  $\|p_i-q_u(t)\|\le R_a$ **at the instant of transmission**. Reachability is
  time-coupled to the trajectory.

---

## 3. The problem

$$
\textbf{(P0)}\quad
\min_{\{q_u,x_u\},\ \tau,\ z}\quad
\mathbb{E}\big[\,T\,\big]
$$

subject to

$$
\begin{aligned}
&\text{(deliver)} && F_{j(v)}(T_{\text{srv}})=\mathcal{D},\quad j(v)=\arg\min_i\|p_i-v\|\\
&\text{(report)} && \text{a REPORT carrying } z \text{ reaches } b \text{ by } T\\
&\text{(accuracy)} && \varrho\big(\|z-v\|\big)\le \epsilon\\
&\text{(energy)} && \textstyle\sum_u\int_0^T P(\|\dot q_u\|)\,dt\le E_{\max}\\
&\text{(kinematics)} && \|\dot q_u\|\le V,\ q_u(0)=q_u(T)=b\\
&\text{(causality)} && \tau \text{ is a stopping time w.r.t. } \{\mathcal{I}_c(t)\},\quad z\in\sigma(\mathcal{I}_c(\tau))
\end{aligned}
$$

Three modelling choices worth defending:

1. **$T$ is the makespan to *all UAVs home and reported*, not time-to-detect.**
   A rescue mission is not finished when a UAV knows something; it is finished
   when the base station does.
2. **$\varrho$ should be a risk measure, not an expectation.** The measurements
   show cooperation moves the **p90** error by −29 % while moving the median by
   a small amount ($\delta=-0.159$). Taking $\varrho=\mathrm{CVaR}_{0.9}$ makes
   the objective sensitive to exactly the thing cooperation buys; taking
   $\varrho=\mathbb{E}$ makes cooperation look worthless. **The choice of risk
   measure decides whether the cooperative scheme has a purpose.**
3. **The causality constraint is what makes this a control problem** rather than
   a planning problem: $\tau$ and $z$ must be measurable w.r.t. information that
   has physically arrived.

**Hardness.** Even the static restriction — pick hover points covering all
$p_i$ within $R_a$ — is geometric set cover (NP-hard); adding the tour gives TSP
with neighbourhoods. (P0) additionally has a continuous-state partially observed
component, so it is a POMDP; exact solution is intractable and the useful work
is in principled restrictions.

---

## 4. The binding constraint the experiments found

For a summon issued at $\tau$ by node $\ell$ to be *actuated*, the aim point must
physically reach an actuator. With a beacon quota $B$ at interval $\Delta$:

$$
\textbf{(R)}\qquad \exists\,u\in\mathcal{M},\ \exists\,t\in[\tau,\ \tau+B\Delta]\ :\quad \big\|q_u(t)-p_\ell\big\|\le R_a
$$

**This is a rendezvous constraint in time and space, and it is the one that
binds.** At 40×40 (780×780 m) the cooperative scheme computed a correct aim —
9 m from the true victim, at $\tau=66$ s — and (R) was violated: the nearest UAV
did not pass within $R_a$ until $\approx 250\text{ s} \gg \tau+B\Delta$. Victim
served in **0/5** seeds despite a perfect estimate.

Two ways to satisfy (R):

- **By construction (closed-loop).** Transmit *only* when a UAV is in range. The
  node echoes because a UAV just cued it, so $\rho>0$ holds at the transmit
  instant and (R) is satisfied trivially. Cost: $\mathcal{I}$ is restricted to
  what one UAV overheard — a strictly smaller information set, hence the worse
  tail.
- **By conditioning (the fix adopted).** Keep the multi-hop information plane,
  but make the *transmission instants* a function of observed UAV presence: a
  leader re-announces whenever it receives a CUE chunk, since a received chunk is
  a certificate that $\rho(q_u(t),p_\ell)>0$ now. This satisfies (R) without
  shrinking $\mathcal{I}$. Result: **0/5 → 5/5**.

Formally, the second is a change of the transmit schedule from open-loop
$t\in\{\tau+k\Delta\}$ to the **event-driven** stopping-time family
$t\in\{s:\ \text{CUE received at }s\}$, which is measurable w.r.t. the node's own
observations. That is the theoretical content of the fix.

---

## 5. Tractable restrictions, and what each scheme solves

**(P1) Blind coverage — `nocoop`, `tsp-mc`.** Drop all information terms; require
every node served:

$$\min_{\{q_u\}} T \quad\text{s.t.}\quad F_i(T)=\mathcal{D}\ \ \forall i\in\mathcal{N}$$

A covering tour problem. `tsp-mc` is Zeng–Xu–Zhang's version: minimum-disk VBS
placement + TSP over the disks + a fly-hover dwell sized to the multicast
recovery time. Optimal for what it optimizes; it never forms $z$ at all, so the
accuracy constraint is infeasible for it by construction.

**(P2) Myopic closed loop — `closed-loop`.** Restrict $\mathcal{I}$ to one-hop
receptions and let $\tau$ be the first time the running argmax stops improving:

$$z=\tilde p_{i^\star},\quad i^\star=\arg\max\{e_i:\ i\ \text{overheard by } u\},\qquad
\tau=\inf\{t:\ \sup_i e_i \text{ unchanged on } [t-\Delta_s,t]\}$$

Satisfies (R) by construction; cheap; but $\mathcal{I}$ is small, so the error
tail is heavy.

**(P3) Cooperative estimate — `proposed`.** Enlarge $\mathcal{I}$ by multi-hop
aggregation, then solve the same stopping/aiming problem on the larger set:

$$z=\arg\max_{i\in\mathcal{C}\cup\partial\mathcal{C}} e_i,\qquad
\tau=\inf\{t: \text{cell aggregate stationary on } [t-\Delta_s,t]\}$$

with $\mathcal{C}$ the cell and $\partial\mathcal{C}$ the peaks shared by
neighbouring cells. Pays $O(|\mathcal{E}|)$ control packets for a larger
$\mathcal{I}$; buys tail accuracy; must additionally enforce (R) explicitly.

**(P4) Optimal stopping — the sub-problem worth isolating.** Given a fixed
trajectory family and the evidence process $\{e_i(t)\}$, choose $\tau$ to solve

$$\min_\tau\ \ \mathbb{E}\big[\alpha\,\tau + \varrho(\|z_\tau-v\|)\big]$$

Waiting improves $\mathcal{I}$ (more nodes cued and reporting) but delays
delivery — and, because of (R), waiting past the sweep can make actuation
*impossible*. So the feasible set for $\tau$ is itself trajectory-dependent:

$$\tau\in\Big[\,\underline\tau,\ \sup\{t:\ \text{(R) satisfiable}\}\Big]$$

The measured version of this: a fixed 45 s window is optimal at 16×16 and yields
**zero** localizations at 8×8, because the upper limit above scales with the
field while a wall-clock constant does not. The adaptive rule (fire when the
leader's own evidence is stationary) is a data-driven surrogate for the true
optimal stopping rule.

---

## 6. Where the interesting open questions are

1. **Characterize (R)'s feasible set.** Given $m$ UAVs on a coverage tour of a
   region of area $|\mathcal{A}|$, what is $\Pr[\text{(R) holds}]$ as a function
   of $|\mathcal{A}|$, $m$, $V$, $R_a$, $B\Delta$? This predicts the scale at
   which the cooperative scheme fails, which we currently only know empirically.
2. **The right risk measure.** State the accuracy objective as
   $\mathrm{CVaR}_\beta$ and derive the $\beta$ above which cooperation is
   justified. The data says cooperation is worth it at $\beta=0.9$ and not at
   $\beta=0.5$; there is a crossover and it is computable.
3. **A CRLB for $z$.** With $\kappa_i=g(\|p_i-v\|)+\varepsilon_i$ and GPS noise,
   the Fisher information for $v$ from a reporting set $\mathcal{R}$ is
   available in closed form. Both current estimators (argmax, weighted centroid)
   are crude; the gap to the bound is unmeasured and is the honest way to justify
   or discard the estimator contribution.
4. **Joint trajectory–stopping design.** (P4) assumes a fixed trajectory. The
   real problem couples them: the tour determines when evidence appears *and*
   when (R) is satisfiable. A receding-horizon formulation over
   $(q_u,\tau)$ jointly is the natural next model.
5. **The coverage/availability tension, observed but unresolved.** Splitting cue
   coverage across all $m$ airframes speeds coverage (good at 40×40: 396→224 s)
   but makes coverage depend on UAVs that get diverted away (catastrophic at
   16×16: victim served 90 %→42.5 %). Formally: a UAV assigned both a covering
   role and an on-demand delivery role has a non-stationary availability, and
   the covering problem must be solved under that. This is a clean, unsolved
   sub-problem.
