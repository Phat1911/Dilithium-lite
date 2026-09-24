# Dilithium-Lite: Building (and Breaking) a Post-Quantum Signature Scheme From Scratch

> A small, from-scratch implementation of CRYSTALS-Dilithium (ML-DSA), built to
> answer one question by experiment rather than by reading: **why does this
> scheme's security actually reduce to a hard lattice problem, and what does a
> real forgery attack look like when the scheme is built wrong?**

## Why this project

RSA and ECDSA — the signature schemes securing almost every blockchain wallet
today — are efficiently breakable by a sufficiently large quantum computer via
Shor's algorithm. Lattice-based schemes like Dilithium (now standardized by
NIST as ML-DSA) are the leading replacement. As someone working in
blockchain/smart contract infrastructure, I wanted to understand this
migration path at the level of "I implemented it and tried to break it,"
not just "I read that it's quantum-resistant."

This repo implements a deliberately shrunk version of Dilithium — small enough
that every matrix, polynomial, and intermediate value can be printed and
checked by hand — and includes a working demonstration of the exact
forgery-to-attack reduction that the scheme's security proof relies on.

**Full technical spec:** [`spec.md`](./spec.md)
**Build plan / milestones:** [`plan.md`](./plan.md)

## What's actually in here

- **Ring arithmetic** over `Z_q[X]/(X^n+1)` — the polynomial ring Dilithium
  computes in, implemented from scratch (no crypto libraries).
- **KeyGen** — produces a genuine Module-LWE sample as the public key.
- **Sign / Verify** — a full Fiat-Shamir-with-aborts signing loop, including
  real rejection sampling (with restart-rate logging).
- **The attack** — a deliberately broken variant of the signer (skipping
  rejection sampling / reusing randomness), plus a script that takes two
  forged-looking signatures and algebraically extracts a short vector solving
  a Module-SIS instance — i.e., reproduces *why* skipping that one safety
  check breaks the whole scheme.
- **A size comparison** against ECDSA, showing concretely why post-quantum
  signatures are bulkier — and what that means for blockchain infra
  (transaction size, gas costs, wallet formats).

## Quick start

```bash
git clone <repo>
cd dilithium-lite
python -m pip install -r requirements.txt
python demo.py          # runs KeyGen → Sign → Verify on a sample message
python attack_demo.py   # reproduces the forgery → SIS-solution extraction
```

## What this is *not*

This is a **learning artifact, not a production library.** Parameters are
shrunk far below any real security level, there's no side-channel resistance,
and none of this should be used to sign anything real. The value here is
pedagogical: a working, inspectable model of *why* Dilithium is designed the
way it is, and *what specifically goes wrong* if a well-known safety step is
omitted.

## Background reading / what I worked through to get here

Before writing any code, I worked through: lattice fundamentals (SVP, CVP,
lattice determinants), the LWE and SIS hardness assumptions, polynomial rings
and NTRU as a bridge into ring-based lattice crypto, and the full Dilithium
sign/verify/security argument — including hand-deriving the exact algebraic
steps that turn a signature forgery into a Module-SIS solution. That
derivation is what `attack_demo.py` reproduces numerically.

## Context: why this matters for blockchain

Ethereum and other chains are actively researching post-quantum migration
paths (account abstraction-based signature swaps, hash-based fallback
signatures) precisely because the signature scheme securing a wallet is one
of the first things a scaled quantum computer would target. Understanding the
actual mechanics — not just the headline "lattice replaces elliptic curves" —
is what this project is meant to build.
