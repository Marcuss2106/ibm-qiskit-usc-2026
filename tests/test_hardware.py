"""Hardware pipeline: circuits reproduce the ideal table when simulated exactly (no network)."""

import numpy as np
from qiskit.quantum_info import Statevector

from qemcmc import hardware as hw


def test_prepared_circuits_match_ideal_table():
    p = hw.problem()
    Qi = hw.ideal_table(p)
    starts = [0, 17, 34]
    for r, qc in zip(starts, hw.build_circuits(p, starts)):
        probs = Statevector(qc.remove_final_measurements(inplace=False)).probabilities()
        assert np.allclose(probs[p["space"].ints], Qi[r], atol=1e-10)
        assert np.isclose(probs.sum(), 1.0)


def test_measured_table_maps_keys_to_ranks():
    p = hw.problem()
    sp = p["space"]
    key = format(int(sp.ints[5]), f"0{hw.NV}b")
    rec = {"starts": [5], "shots": 100, "counts": [{key: 60, "0000000": 40}]}
    Q = hw.measured_table(rec, p)
    assert np.isclose(Q[0, 5], 0.6) and np.isclose(Q.sum(), 0.6)  # invalid key dropped
