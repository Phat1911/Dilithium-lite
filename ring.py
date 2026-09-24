"""Naive arithmetic for the toy Dilithium ring Z_q[X] / (X^n + 1)."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeAlias

Polynomial: TypeAlias = tuple[int, ...]
Matrix: TypeAlias = tuple[tuple[Polynomial, ...], ...]


class Ring:
    """Arithmetic in ``Z_q[X] / (X^n + 1)`` using centered coefficients."""

    def __init__(self, n: int = 8, q: int = 17) -> None:
        if n <= 0:
            raise ValueError("n must be positive")
        if q <= 1 or q % 2 == 0:
            raise ValueError("q must be an odd modulus")
        if q % (2 * n) != 1:
            raise ValueError("q must satisfy q == 1 (mod 2n)")
        self.n = n
        self.q = q

    def _check_poly(self, a: Sequence[int]) -> None:
        if len(a) != self.n:
            raise ValueError(f"polynomial must have exactly {self.n} coefficients")

    def reduce_coeff(self, value: int) -> int:
        half = self.q // 2
        return (value + half) % self.q - half

    def normalize(self, a: Sequence[int]) -> Polynomial:
        self._check_poly(a)
        return tuple(self.reduce_coeff(value) for value in a)

    def add(self, a: Sequence[int], b: Sequence[int]) -> Polynomial:
        self._check_poly(a)
        self._check_poly(b)
        return tuple(self.reduce_coeff(x + y) for x, y in zip(a, b))

    def sub(self, a: Sequence[int], b: Sequence[int]) -> Polynomial:
        self._check_poly(a)
        self._check_poly(b)
        return tuple(self.reduce_coeff(x - y) for x, y in zip(a, b))

    def mul(self, a: Sequence[int], b: Sequence[int]) -> Polynomial:
        """Multiply and reduce with ``X^n = -1``."""
        self._check_poly(a)
        self._check_poly(b)
        coefficients = [0] * (2 * self.n - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                coefficients[i + j] += x * y
        result = coefficients[: self.n]
        for degree in range(self.n, 2 * self.n - 1):
            result[degree - self.n] -= coefficients[degree]
        return tuple(self.reduce_coeff(value) for value in result)

    def sample_small(self, bound: int, rng: random.Random | None = None) -> Polynomial:
        if bound < 0:
            raise ValueError("bound must be non-negative")
        generator = rng or random
        return tuple(generator.randint(-bound, bound) for _ in range(self.n))

    def sample_challenge(self, tau: int, rng: random.Random | None = None) -> Polynomial:
        if not 0 <= tau <= self.n:
            raise ValueError("tau must be between 0 and n")
        generator = rng or random
        positions = generator.sample(range(self.n), tau)
        result = [0] * self.n
        for position in positions:
            result[position] = generator.choice((-1, 1))
        return tuple(result)

    def vector_add(self, a: Sequence[Polynomial], b: Sequence[Polynomial]) -> tuple[Polynomial, ...]:
        if len(a) != len(b):
            raise ValueError("vectors must have the same length")
        return tuple(self.add(x, y) for x, y in zip(a, b))

    def matrix_vector_mul(self, matrix: Matrix, vector: Sequence[Polynomial]) -> tuple[Polynomial, ...]:
        if not matrix:
            return ()
        columns = len(matrix[0])
        if columns != len(vector) or any(len(row) != columns for row in matrix):
            raise ValueError("matrix and vector dimensions do not agree")
        zero = (0,) * self.n
        output = []
        for row in matrix:
            value = zero
            for coefficient, entry in zip(row, vector):
                value = self.add(value, self.mul(coefficient, entry))
            output.append(value)
        return tuple(output)


DEFAULT_RING = Ring()


def add(a: Sequence[int], b: Sequence[int]) -> Polynomial:
    return DEFAULT_RING.add(a, b)


def mul(a: Sequence[int], b: Sequence[int]) -> Polynomial:
    return DEFAULT_RING.mul(a, b)


def sample_small(bound: int, rng: random.Random | None = None) -> Polynomial:
    return DEFAULT_RING.sample_small(bound, rng)


def sample_challenge(tau: int, rng: random.Random | None = None) -> Polynomial:
    return DEFAULT_RING.sample_challenge(tau, rng)
