# Reconstruction Notes

This repository is a **faithful reconstruction** of the paper, not a claim of direct access to the authors' original source code.

## Explicitly underspecified items in the paper text

The manuscript excerpt does not fully specify:

1. the exact formula for Eq. (18) and Eq. (19), although their semantic role is described;
2. the exact discretization or hashing scheme used for the Tier-1 table;
3. the exact network architecture of every Tier-2 executor beyond MLP depth/width hints;
4. the exact message encoding semantics of the 8-bit coalition messages;
5. the exact offline replay alarm-generation procedure;
6. the exact subcoalition set used in every core-feasibility evaluation;
7. complete numerical values for figure-only ablations where tables were not included in the excerpt.

## How those gaps were handled

### Meta reward

Implemented as:

- discounted environment return over the option horizon,
- plus a small internal-guidance term based on simple evidence heuristics.

### Execution reward

Implemented as a combination of:

- coalition-level mission/risk term,
- per-action cost regularization,
- optional feasibility penalties.

### Tier-1 state abstraction

Implemented via a stable JSON serialization + bounded hashing of feature groups.

### Message fusion

Implemented as an 8-bit message vector concatenated with local feature summaries.

### Offline replay

Implemented as event-window classification / progression scoring over normalized telemetry windows.

## Recommendation for a real reproduction campaign

If exact reproduction is the goal, the next practical step would be to obtain or verify:

- the original observation encoder,
- the exact Tier-2 action parameter domains,
- the exact internal-guidance formula,
- the exact core-allocation procedure,
- the exact preprocessing scripts for LANL and DARPA.
