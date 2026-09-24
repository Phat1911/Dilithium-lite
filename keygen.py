"""Key generation for the toy Dilithium-Lite scheme."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ring import Matrix, Polynomial, Ring


@dataclass(frozen=True)
class PublicKey:
    """Public key components."""

    A: Matrix
    t: tuple[Polynomial, ...]


@dataclass(frozen=True)
class SecretKey:
    """Secret key components, retaining the public values for verification."""

    A: Matrix
    t: tuple[Polynomial, ...]
    s1: tuple[Polynomial, ...]
    s2: tuple[Polynomial, ...]


@dataclass(frozen=True)
class KeyPair:
    public_key: PublicKey
    secret_key: SecretKey


class KeyGenerator:
    """Generate toy Module-LWE key pairs over a :class:`ring.Ring`."""

    def __init__(
        self,
        ring: Ring | None = None,
        *,
        k: int = 2,
        l: int = 2,
        eta: int = 2,
        rng: random.Random | None = None,
    ) -> None:
        if k <= 0 or l <= 0:
            raise ValueError("k and l must be positive")
        if eta < 0:
            raise ValueError("eta must be non-negative")
        self.ring = ring or Ring()
        self.k = k
        self.l = l
        self.eta = eta
        self.rng = rng

    def sample_matrix(self) -> Matrix:
        """Sample a ``k × l`` matrix uniformly from ``R_q``."""
        generator = self.rng or random
        return tuple(
            tuple(
                self.ring.normalize(
                    tuple(generator.randrange(self.ring.q) for _ in range(self.ring.n))
                )
                for _ in range(self.l)
            )
            for _ in range(self.k)
        )

    def generate(self) -> KeyPair:
        """Generate ``A``, small secrets, and ``t = A·s1 + s2``."""
        s1 = tuple(self.ring.sample_small(self.eta, self.rng) for _ in range(self.l))
        s2 = tuple(self.ring.sample_small(self.eta, self.rng) for _ in range(self.k))
        matrix = self.sample_matrix()
        product = self.ring.matrix_vector_mul(matrix, s1)
        t = self.ring.vector_add(product, s2)
        public_key = PublicKey(A=matrix, t=t)
        secret_key = SecretKey(A=matrix, t=t, s1=s1, s2=s2)
        return KeyPair(public_key=public_key, secret_key=secret_key)


def keygen(
    *,
    ring: Ring | None = None,
    k: int = 2,
    l: int = 2,
    eta: int = 2,
    rng: random.Random | None = None,
) -> KeyPair:
    """Convenience wrapper for :class:`KeyGenerator` with toy defaults."""
    return KeyGenerator(ring, k=k, l=l, eta=eta, rng=rng).generate()
