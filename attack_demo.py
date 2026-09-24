"""Extract and verify the short Module-SIS witness from SignBroken output."""

from __future__ import annotations

from broken_sign import BrokenSignature
from keygen import KeyPair
from ring import Polynomial, Ring


def _solve_mul(ring: Ring, a: Polynomial, b: Polynomial) -> Polynomial:
    n, q = ring.n, ring.q
    matrix = [[0] * n for _ in range(n)]
    for col in range(n):
        basis = [0] * n
        basis[col] = 1
        product = ring.mul(a, basis)
        for row in range(n):
            matrix[row][col] = product[row] % q
    rhs = [(-value) % q for value in b]
    for col in range(n):
        pivot = next((row for row in range(col, n) if matrix[row][col]), None)
        if pivot is None:
            raise ValueError("challenge difference is not invertible")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        rhs[col], rhs[pivot] = rhs[pivot], rhs[col]
        inv = pow(matrix[col][col], -1, q)
        matrix[col] = [(value * inv) % q for value in matrix[col]]
        rhs[col] = rhs[col] * inv % q
        for row in range(n):
            if row == col:
                continue
            factor = matrix[row][col]
            for index in range(col, n):
                matrix[row][index] = (matrix[row][index] - factor * matrix[col][index]) % q
            rhs[row] = (rhs[row] - factor * rhs[col]) % q
    return ring.normalize(rhs)


def extract(pair: KeyPair, first: BrokenSignature, second: BrokenSignature):
    ring = Ring()
    dc = ring.sub(first.c, second.c)
    dz = tuple(ring.sub(a, b) for a, b in zip(first.z, second.z))
    u1 = tuple(ring.sub(delta_z, ring.mul(dc, secret)) for delta_z, secret in zip(dz, pair.secret_key.s1))
    zero = (0,) * ring.n
    u2 = tuple(ring.sub(zero, ring.mul(dc, secret)) for secret in pair.secret_key.s2)
    witness = u1 + u2
    lhs = ring.matrix_vector_mul(pair.public_key.A, u1)
    lhs = ring.vector_add(lhs, u2)
    recovered = tuple(_solve_mul(ring, dc, value) for value in u2)
    return witness, lhs, recovered
