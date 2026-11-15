# Hardware run: long–short proposal table on ibm_marrakesh (bead 6nz)

**Setup** (`qemcmc/hardware.py`, fixed before running). Market-neutral long–short book,
4 long / 4 short on the 8 core ETFs, window ending 2025-12-31. SPY fixed long; 7 qubits
encode which 3 of the other 7 are long (35 valid books). The instance has 3 local optima;
greedy finds the best book from 46% of starts. Best book: long SPY, IWM, IEF, GLD; short
EFA, EEM, TLT, DBC.

Circuit: palindromic **ordered-ring** XY mixer + **ring** score phase (the hardware-cheap
variant), β = 0.75, g = 1 (chosen in `experiments/longshort/fair_tuning.py`). One circuit
per starting book: X gates for its longs, the circuit, measurement. Compiled at
optimization level 3: **86 two-qubit gates, two-qubit depth 83**. SamplerV2, dynamical
decoupling on, no other mitigation.

```bash
python -m qemcmc.hardware dry   --backend fake_fez                       # noisy simulation
python -m qemcmc.hardware pilot --backend ibm_marrakesh --starts 0 17 34 # 2 QPU-seconds
python -m qemcmc.hardware full  --backend ibm_marrakesh --shots 1024     # 12 QPU-seconds
python -m qemcmc.hardware analyze results/hardware/<file>.json
```

Jobs (2026-11-15 UTC): pilot `dbsiegok09pc73b074jg` (3 starts × 256 shots, 2 s); full
`dbsiephabdes73fr6n4g` (35 starts × 1,024 shots, **12 QPU-seconds**). Shots were raised
from the planned 256 to 1,024 after the pilot showed only ~45% usable shots. Account:
14 of 600 seconds used. Raw counts and metadata: `results/hardware/`.

## Results (full table)

| Metric | Hardware (Marrakesh) | Noisy simulation (FakeFez, 256 shots) | Shots only (no device noise) |
|---|---|---|---|
| Usable shots (exactly 4 long) | **43%** (min 40%) | 77% | 100% |
| Distance to ideal proposals among valid outcomes (TVD, median per start) | **0.20** | 0.15 | 0.09 at 1,024 shots |
| Asymmetry of the proposal table | **0.33** | 0.41 (0.35 from shots) | 0.16 |
| Spectral gap of the resulting Metropolis chain | **0.043** | 0.069 | 0.088 |
| Bias of where the chain settles (TVD to target distribution) | **0.048** | 0.090 | 0.062 |
| Chain's probability of the best book (target 0.231) | **0.208** | 0.236 | — |

Reference gaps, same instance and temperature: ideal circuit 0.090, single-swap
Metropolis 0.061.

## What it shows

1. **The circuit runs and keeps its structure.** Of valid outcomes, the distribution is
   measurably distorted (TVD 0.20 vs 0.09 from shots alone) but recognisably the ideal one.
2. **Noise mostly ejects outcomes from the valid subspace.** 57% of shots have the wrong
   number of longs; the simulator's noise model predicted 23%. Wrong-count outcomes are
   rejected attempts, which slows the chain.
3. **The chain stays nearly correct.** The device breaks proposal symmetry (asymmetry
   0.33 vs 0.16 from shots), but the hardware chain still settles close to the target
   distribution (bias 0.048; best-book probability 0.21 vs 0.23), because acceptance uses
   exact scores.
4. **Mixing does not survive the noise.** The hardware chain's gap (0.043) is half the
   ideal circuit's (0.090) and **below single-swap Metropolis (0.061)**: on hardware,
   today, the quantum proposal mixes slower than the simplest classical move.

**Caveats.** One instance, one device, one day; small problem (35 books); hardware-cheap
circuit only (the complete-mixer circuit that beat multi-swap in simulation needs about
540 two-qubit gates and was not run); no error mitigation beyond dynamical decoupling;
per-attempt comparison only (each hardware attempt also costs a shot and a job).
