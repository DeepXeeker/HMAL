# Deep Analysis of the Paper and Repository Mapping

## 1. Proposed model: what the paper is actually building

The paper proposes a **layered defense architecture** with two strongly coupled components:

1. **Strategic layer**: a deception-aware hypergame between an attacker and a coalition of defenders.
2. **Learning layer**: a hierarchical multi-agent learning controller that operationalizes the strategic model.

The central design idea is not just “HRL for cyber defense.” It is the coupling of:

- **belief mismatch and deception** in the attacker-defender game,
- **coalition stability** among multiple defenders,
- **hierarchical control** for scalable action selection.

### 1.1 Strategic formulation

The paper defines the overall model as:

- an **adversarial layer** `G_adv`, capturing attacker vs defender interaction under distorted observations;
- a **coalition layer** `G_coal`, capturing information sharing, utility allocation, and core feasibility.

This is important because the learning agent is not supposed to optimize defense in a vacuum. It is supposed to optimize **only those actions that remain feasible under coalition commitments and disruption budgets**.

### 1.2 HMAL controller

The learning controller is explicitly hierarchical.

#### Tier-1: mode selector

Tier-1 chooses a high-level mode from:

- `Sense`
- `Deceive`
- `Recover`
- `Idle`

The paper repeatedly frames Tier-1 as small, discrete, and strategically meaningful. That makes a **tabular Q-learning router** a credible reconstruction.

#### Tier-2: specialized executors

Each mode activates a specialist policy that emits a parameterized cyber action.

- `Sense` -> `Monitor`, `Analyse`
- `Deceive` -> `DeployDecoy`
- `Recover` -> `Remove`, `Restore`, `BlockTrafficZone`, `AllowTrafficZone`
- `Idle` -> `Sleep`

The paper clearly prefers **PPO** for Tier-2 because it is more stable than DDPG in nonstationary adversarial environments and simpler than TRPO.

### 1.3 Shared observation pipeline

The paper defines the shared information state as six grouped feature families:

- host
- interface
- process
- session
- system
- user

This interface is reused by both tiers. In practice, that means the repository should not build separate feature pipelines for the selector and the executors. It should build one fused belief/profile representation and expose it everywhere.

### 1.4 Distortion-aware observation model

The hypergame variable `Xi` is operationalized as observation corruption:

- event subsampling
- delay
- source dropout
- message corruption / degradation

This matters because the paper does **not** use distortion only as a theoretical construct. It uses it as a training-time robustness mechanism.

### 1.5 Coalition-aware execution

The coalition layer affects execution in three ways:

1. **message fusion**: 8-bit inter-agent messages are incorporated into the shared belief/profile;
2. **budget checks**: decoy budgets, blocking budgets, and other feasibility constraints are enforced;
3. **stability metrics**: coalition value and payoff allocations are used to test core violations.

This is why the repository includes messaging, budget checks, Shapley approximation, and core-feasibility utilities as first-class components.

## 2. Simulation design

The paper uses **CybORG CC4** as the primary online simulation environment.

### 2.1 Why CC4 fits the paper

CC4 is a segmented enterprise-like network with:

- multiple Blue defenders operating over different zones,
- a Red attacker progressing through the network,
- benign Green traffic that makes disruption costs meaningful,
- restricted communication between Blue defenders.

This is almost tailor-made for the paper’s claims about coalition-constrained defense.

### 2.2 Interaction semantics in the paper

The paper imposes a two-stage abstraction over CC4:

1. Red acts and changes the latent state.
2. Blue receives observations and executes its coalition action.

This matters because the code should make room for option-level credit assignment and delayed effect accumulation, even if the base simulator internally implements a different timing order.

### 2.3 Action abstraction in the paper

The paper does not use raw action names as the main decision language. Instead it creates a hierarchical action abstraction:

- Tier-1 chooses the family.
- Tier-2 chooses the specific action target / parameters.

That is why the repository maintains both:

- a **mode-to-action-family map**, and
- **mode-specific action masking**.

## 3. Datasets used in the paper

The paper uses two empirical datasets outside simulation.

### 3.1 LANL cyber1

LANL is used for:

- distortion calibration,
- validating that the feature interface is realistic,
- offline replay evaluation,
- training-schedule ablations,
- coalition-fusion ablations,
- feasibility-aware execution ablations.

The key role of LANL in the paper is **not** full online control. It is a realistic telemetry benchmark for early malicious progression inference under imperfect sensing.

### 3.2 DARPA Transparent Computing E5

DARPA TC E5 is used for:

- provenance-style host telemetry validation,
- distortion robustness ablation,
- cross-source consistency evaluation,
- offline replay detection benchmarking.

The paper uses DARPA to show that distortion-aware training is not only useful in a simulator but also in heterogeneous provenance data.

## 4. Evaluation metrics

The paper’s metrics are grouped into four coherent families.

### 4.1 Simulation / mission metrics

- mission return
- attacker progression delay
- operational cost
- Blue service interruptions

### 4.2 Detection metrics

- precision
- recall
- F1-score
- AUPRC
- lead time

### 4.3 Coalition metrics

- core violation rate
- violation margin
- cross-zone consistency

### 4.4 Execution quality metrics

- invalid-action rate
- projected service disruption
- episodes to convergence
- seed stability / seed standard deviation

This repository therefore includes a general metrics module rather than a single evaluation function hardcoded only for classification.

## 5. Implementation details that matter for the repo

The paper makes several implementation commitments that directly determine repository structure.

### 5.1 Two algorithm families, not one

- Tier-1 = tabular Q-learning
- Tier-2 = PPO

A clean repository should therefore separate:

- selector code,
- executor code,
- stage-wise training orchestration.

### 5.2 Mode-specific parameterization

Tier-2 is not just a single “policy network.” It is a **policy bank** over specialized branches. That is why the code includes a `Tier2PolicyBank` abstraction.

### 5.3 Bottom-up training

The paper strongly argues that Tier-2 should be trained before Tier-1 so the selector does not chase unstable executor behavior.

That means the repository needs **separate stage scripts**, not just one monolithic trainer.

### 5.4 Feasibility-aware rollout generation

The paper explicitly states that invalid joint actions are filtered during rollout generation. That is stronger than merely adding a reward penalty afterward. Hence the repository implements:

- action masking,
- budget enforcement,
- optional soft penalties.

## 6. Training strategy in the paper

The paper’s training schedule is structurally important.

### Stage I

Independent PPO pretraining for each Tier-2 specialist.

### Stage II

Freeze or nearly freeze executors and train the selector using option-level credit.

### Stage III

Optional alternating refinement to reduce mismatch between routing and execution.

This is one of the clearest parts of the paper and deserves first-class support in the codebase.

## 7. Detailed ablation analysis

## 7.1 Impact of hierarchy modelling

Goal: determine whether performance gains come from hierarchy itself, not merely PPO.

Variants:

- Full HMAL
- Single-tier PPO
- FlatPolicy

Interpretation:

- Full HMAL wins because it separates strategic intent from low-level actuation.
- Single-tier PPO controls for function approximation but still loses, which supports the argument that **hierarchical decomposition** matters.
- FlatPolicy is worst because it merges mode selection and parameter instantiation into a large action space.

Repository implication:

- there must be a clean switch to disable Tier-1,
- a single-tier PPO fallback should exist,
- a flat action-selection mode should exist.

## 7.2 Tier-1 reward and credit assignment

Goal: test whether selector performance depends on correct option-level attribution.

Variants:

- Full Tier-1 Reward
- Immediate Reward Only
- No Internal Guidance
- Uniform Option Credit

Interpretation:

- delayed, multi-step effects of cyber actions make one-step reward too myopic;
- expert-guidance terms help with early routing under ambiguity;
- discounting within the option window is better than uniform credit.

Repository implication:

- meta reward must be modular;
- immediate-only, no-guidance, and uniform-credit variants should be config toggles.

## 7.3 Training-schedule ablation

Goal: test whether the bottom-up schedule is actually necessary.

Variants:

- Full Staged Training
- Joint End-to-End
- No Stage III
- Reverse Order

Interpretation:

- staged training gives the best trade-off between quality and stability;
- joint optimization harms stability;
- Stage III refinement improves balance;
- reverse order is worst because the selector learns over unreliable executors.

Repository implication:

- the runner must support all four schedules via configuration, not code duplication.

## 7.4 Coalition-information fusion

Goal: determine how much inter-zone fusion contributes.

Variants:

- Full Fused Profile
- NoMessage
- Local-only Belief
- Noisy/Delayed Fusion

Interpretation:

- fusion improves recall, lead time, and cross-zone consistency;
- degraded messages make behavior more conservative;
- local-only inference is weak for cross-zone progression.

Repository implication:

- messages, fusion, and message corruption should be first-class components.

## 7.5 Deception capability

Goal: isolate the effect of the Deceive branch.

Variants:

- Full HMAL
- NoDeception
- No Deceive Mode
- Capped Deceive

Interpretation:

- deception materially slows the attacker;
- removing the entire Deceive branch hurts routing more than leaving the branch present but inactive;
- budgeted deception can reduce disruption but also limit effectiveness.

Repository implication:

- deception budget must be configurable;
- `deploy_decoy_enabled` and `deceive_enabled` should be separate toggles.

## 7.6 Distortion-aware observation

Goal: determine whether training over randomized corruption improves robustness.

Variants:

- Full Distortion-Aware Training
- Clean Training
- Fixed Mild Distortion

Interpretation:

- clean training can look best on clean data but collapses under corruption;
- randomized corruption creates the best severe-distortion robustness;
- mild fixed corruption is not enough.

Repository implication:

- distortion sampling must be stochastic and configurable.

## 7.7 Feasibility-aware execution

Goal: test whether validity checks and budget enforcement matter.

Variants:

- Full Feasibility-Aware
- Masking Only
- Budget Only
- Soft-Penalty Only
- No Constraints

Interpretation:

- the best results require both admissibility and coalition-budget enforcement;
- post-hoc penalties are weaker than pre-execution screening;
- unconstrained action selection increases invalid actions and coalition violations.

Repository implication:

- rollout-time checks are essential, not optional cosmetics.

## 8. Repository design decisions justified by the paper

The repository structure is driven directly by the paper’s claims:

- `hmal/agents/` because the paper has two tiers and a policy bank
- `hmal/coalition/` because coalition value and core checks are central contributions
- `hmal/observation/` because the feature interface and distortion model are major ingredients
- `hmal/envs/` because the paper spans both simulation and offline replay
- `configs/ablation/` because ablations are numerous and should be reproducible without code edits
- `paper_results/` because several results are explicitly reported and should be preserved as reference tables

## 9. What the repository can and cannot guarantee

### It can provide

- faithful architectural reconstruction
- explicit support for the paper’s training schedule
- consistent ablation toggles
- ready-to-extend simulation adapters
- offline replay pipelines for LANL and DARPA-style telemetry

### It cannot guarantee without the authors’ original code

- exact numerical reproduction of all reported means and standard deviations
- exact feature engineering choices used by the original authors
- exact hidden state mapping between simulator and telemetry datasets
- exact implementation of equations not fully specified in the manuscript excerpt

That is why `docs/reconstruction_notes.md` is included and why the code is written to be transparent and editable.
