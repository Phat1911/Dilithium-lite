"""Intentionally broken signer for the isolated M4 attack demonstration."""

from __future__ import annotations

import random
from dataclasses import dataclass

from keygen import SecretKey
from ring import Polynomial, Ring
from sign import challenge


@dataclass(frozen=True)
class BrokenSignature:
    y: tuple[Polynomial, ...]
    w: tuple[Polynomial, ...]
    z: tuple[Polynomial, ...]
    c: Polynomial


def sign_pair(secret_key: SecretKey, first: bytes, second: bytes, *, eta: int = 2,
              tau: int = 2, rng: random.Random | None = None):
    """Return two signatures with the same commitment, intentionally broken."""
    ring = Ring()
    zero = (0,) * ring.n
    w = tuple(zero for _ in range(len(secret_key.s2)))

    def solve_matrix(target):
        rows, cols, q = len(secret_key.A) * ring.n, len(secret_key.s1) * ring.n, ring.q
        aug = [[0] * (cols + 1) for _ in range(rows)]
        for row, matrix_row in enumerate(secret_key.A):
            for col, entry in enumerate(matrix_row):
                for i in range(ring.n):
                    basis = [0] * ring.n; basis[i] = 1
                    product = ring.mul(entry, basis)
                    for j, value in enumerate(product):
                        aug[row * ring.n + j][col * ring.n + i] = value % q
            for j, value in enumerate(target[row]):
                aug[row * ring.n + j][-1] = value % q
        pivot_row = 0
        for col in range(cols):
            pivot = next(row for row in range(pivot_row, rows) if aug[row][col])
            aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
            inv = pow(aug[pivot_row][col], -1, q)
            aug[pivot_row] = [(v * inv) % q for v in aug[pivot_row]]
            for row in range(rows):
                if row != pivot_row and aug[row][col]:
                    factor = aug[row][col]
                    aug[row] = [(a - factor * b) % q for a, b in zip(aug[row], aug[pivot_row])]
            pivot_row += 1
        return tuple(ring.normalize(aug[col * ring.n:(col + 1) * ring.n][-1:] and [aug[col * ring.n + i][-1] for i in range(ring.n)]) for col in range(cols // ring.n))

    messages = [first, second]
    outputs = []
    while True:
        outputs = []
        for message in messages:
            c = challenge(ring, w, message, tau)
            target = tuple(ring.mul(c, value) for value in secret_key.t)
            z = solve_matrix(target)
            outputs.append(BrokenSignature(y=z, w=w, z=z, c=c))
        dc = ring.sub(outputs[0].c, outputs[1].c)
        matrix = [[0] * ring.n for _ in range(ring.n)]
        for col in range(ring.n):
            basis = [0] * ring.n; basis[col] = 1
            product = ring.mul(dc, basis)
            for row, value in enumerate(product): matrix[row][col] = value % ring.q
        rank = 0
        for col in range(ring.n):
            pivot = next((row for row in range(rank, ring.n) if matrix[row][col]), None)
            if pivot is None: break
            matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
            inv = pow(matrix[rank][col], -1, ring.q)
            matrix[rank] = [(v * inv) % ring.q for v in matrix[rank]]
            for row in range(ring.n):
                if row != rank and matrix[row][col]:
                    f = matrix[row][col]
                    matrix[row] = [(a - f * b) % ring.q for a, b in zip(matrix[row], matrix[rank])]
            rank += 1
        if rank == ring.n and outputs[0].c != outputs[1].c:
            break
        messages[1] += b"!"
    return outputs[0], outputs[1]
