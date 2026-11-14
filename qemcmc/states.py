"""Canonical numbering of valid portfolios (bit strings with exactly k ones).

Three equivalent labels for a portfolio:

- rank: position 0..C(n,k)-1 in lexicographic order of the held-ETF index
  tuples (itertools.combinations order). Use this to index proposal tables.
- combo: sorted tuple of held ETF indices, e.g. (0, 4, 5).
- int: integer with bit i set when ETF i is held. This matches Qiskit's
  measurement keys: qubit i is ETF i and int(key, 2) gives this integer, so
  format(value, f"0{n}b") is the Qiskit bit string (qubit 0 rightmost).
"""

from __future__ import annotations

from itertools import combinations
from math import comb

import numpy as np


class StateSpace:
    """All C(n, k) valid portfolios with rank/combo/bits/int conversions."""

    def __init__(self, n: int, k: int):
        if not 0 < k < n <= 62:
            raise ValueError(f"need 0 < k < n <= 62, got n={n}, k={k}")
        self.n, self.k = n, k
        size = comb(n, k)
        flat = np.fromiter(
            (i for c in combinations(range(n), k) for i in c),
            dtype=np.int64,
            count=size * k,
        )
        self.combos = flat.reshape(size, k)  # [C, k], rank order
        self.bits = np.zeros((size, n), dtype=np.int8)  # [C, n]
        np.put_along_axis(self.bits, self.combos, 1, axis=1)
        self.ints = (np.int64(1) << self.combos).sum(axis=1)  # [C]
        self._order = np.argsort(self.ints)
        self._sorted_ints = self.ints[self._order]

    @property
    def size(self) -> int:
        return len(self.combos)

    def is_valid_int(self, value) -> np.ndarray:
        """True where the integer has exactly k bits set within n bits."""
        v = np.asarray(value, dtype=np.int64)
        i = np.searchsorted(self._sorted_ints, v).clip(max=self.size - 1)
        return self._sorted_ints[i] == v

    def rank_of_int(self, value) -> np.ndarray:
        """Rank for each valid integer; raises on any invalid one."""
        v = np.asarray(value, dtype=np.int64)
        if not self.is_valid_int(v).all():
            raise ValueError("integer(s) without exactly k of n bits set")
        return self._order[np.searchsorted(self._sorted_ints, v)]

    def rank_of_combo(self, combo) -> int:
        return int(self.rank_of_int(sum(1 << int(i) for i in combo)))

    def rank_of_bits(self, bits) -> int:
        b = np.asarray(bits)
        return int(self.rank_of_int(int((b.astype(np.int64) << np.arange(self.n)).sum())))

    def swap_neighbors(self) -> np.ndarray:
        """Ranks reachable by one swap (local Kawasaki move). Shape [C, k(n-k)].

        Column j*(n-k) + m swaps out the j-th held ETF (ascending) for the m-th
        unheld ETF (ascending). Cached after the first call.
        """
        if getattr(self, "_neighbors", None) is None:
            n, k = self.n, self.k
            unheld = np.argsort(self.bits, axis=1, kind="stable")[:, : n - k]
            one = np.int64(1)
            flip = (one << self.combos)[:, :, None] | (one << unheld)[:, None, :]
            nbr_ints = (self.ints[:, None, None] ^ flip).reshape(self.size, -1)
            self._neighbors = self.rank_of_int(nbr_ints)
        return self._neighbors

    def bitstring(self, rank: int) -> str:
        """Qiskit-order bit string (ETF 0 is the rightmost character)."""
        return format(int(self.ints[rank]), f"0{self.n}b")
