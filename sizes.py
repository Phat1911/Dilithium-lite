"""Toy key/signature size accounting and optional ECDSA comparison."""

from __future__ import annotations

from keygen import keygen
from sign import Signature, Signer
import random


def _poly_bytes(poly) -> int:
    return 2 * len(poly)


def toy_sizes(pair=None, signature: Signature | None = None) -> dict[str, int]:
    pair = pair or keygen()
    if signature is None:
        signature = Signer(pair.secret_key, rng=random.Random(0)).sign(b"size sample")
        signature_bytes = sum(_poly_bytes(poly) for poly in signature.z) + _poly_bytes(signature.c)
        signature_bytes += len(signature.w or ()) * 0
    else:
        signature_bytes = sum(_poly_bytes(poly) for poly in signature.z) + _poly_bytes(signature.c)
    public_bytes = sum(_poly_bytes(poly) for row in pair.public_key.A for poly in row)
    public_bytes += sum(_poly_bytes(poly) for poly in pair.public_key.t)
    return {"public_key": public_bytes, "signature": signature_bytes}


def comparison_table() -> list[dict[str, int | str]]:
    toy = toy_sizes()
    return [
        {"scheme": "Dilithium-Lite toy", "public_key_bytes": toy["public_key"], "signature_bytes": toy["signature"]},
        {"scheme": "ECDSA secp256k1 (typical raw)", "public_key_bytes": 33, "signature_bytes": 64},
        {"scheme": "ML-DSA-65 reference", "public_key_bytes": 1952, "signature_bytes": 3293},
    ]


if __name__ == "__main__":
    for row in comparison_table():
        print(row)
