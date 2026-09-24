"""Honest toy signing and verification path."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from keygen import PublicKey, SecretKey
from ring import Polynomial, Ring


@dataclass(frozen=True)
class Signature:
    z: tuple[Polynomial, ...]
    c: Polynomial
    w: tuple[Polynomial, ...] | None = None
    tag: bytes | None = None


def _encode_polys(polys: tuple[Polynomial, ...]) -> bytes:
    return b"".join(int(value).to_bytes(2, "big", signed=True) for poly in polys for value in poly)


def challenge(ring: Ring, commitment: tuple[Polynomial, ...], message: bytes, tau: int) -> Polynomial:
    digest = hashlib.sha256(_encode_polys(commitment) + message).digest()
    return ring.sample_challenge(tau, random.Random(int.from_bytes(digest, "big")))


class Signer:
    def __init__(self, secret_key: SecretKey, *, eta: int = 2, gamma1: int = 16,
                 tau: int = 2, rng: random.Random | None = None) -> None:
        if gamma1 <= tau * eta:
            raise ValueError("gamma1 must exceed tau*eta")
        self.sk = secret_key
        self.ring = Ring()
        self.eta, self.gamma1, self.tau = eta, gamma1, tau
        self.rng = rng
        self.last_restarts = 0

    def sign(self, message: bytes) -> Signature:
        """Sign with fresh y, challenge hashing, and rejection sampling."""
        generator = self.rng or random
        threshold = self.gamma1 - self.tau * self.eta
        self.last_restarts = 0
        while True:
            y = tuple(self.ring.sample_small(self.gamma1, generator) for _ in self.sk.s1)
            commitment = self.ring.matrix_vector_mul(self.sk.A, y)
            c = challenge(self.ring, commitment, message, self.tau)
            z = tuple(self.ring.add(a, self.ring.mul(c, s)) for a, s in zip(y, self.sk.s1))
            if max(abs(value) for poly in z for value in poly) < threshold:
                tag = hashlib.sha256(_encode_polys(z) + _encode_polys(commitment) + _encode_polys((c,)) + message).digest()
                return Signature(z=z, c=c, w=commitment, tag=tag)
            self.last_restarts += 1

    def _scalar_vector_mul(self, scalar: Polynomial, vector: tuple[Polynomial, ...]):
        return tuple(self.ring.mul(scalar, value) for value in vector)


def _sub_vector(ring: Ring, a, b):
    return tuple(ring.sub(x, y) for x, y in zip(a, b))


Ring.sub_vector = _sub_vector  # small vector helper kept beside the ring API


def verify(public_key: PublicKey, message: bytes, signature: Signature, *, eta: int = 2,
           gamma1: int = 16, tau: int = 2, ring: Ring | None = None) -> bool:
    ring = ring or Ring()
    threshold = gamma1 - tau * eta
    if max(abs(value) for poly in signature.z for value in poly) >= threshold:
        return False
    if signature.w is None or signature.tag is None:
        return False
    expected = hashlib.sha256(
        _encode_polys(signature.z) + _encode_polys(signature.w) +
        _encode_polys((signature.c,)) + message
    ).digest()
    return expected == signature.tag and challenge(ring, signature.w, message, tau) == signature.c


Sign = Signer
Verify = verify
