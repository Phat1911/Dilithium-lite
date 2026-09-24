# SPEC.md — Dilithium-Lite: A Toy Lattice Signature Scheme

## 1. Purpose

A from-scratch, small-parameter reimplementation of the CRYSTALS-Dilithium (ML-DSA)
signature scheme, built to verify by direct experiment — not just by reading — why
its security reduces to the Module-SIS and Module-LWE hardness assumptions.

This is **not** a production or side-channel-safe implementation. Parameters are
deliberately shrunk so every intermediate value can be printed, inspected, and
reasoned about by hand.

## 2. Parameters

| Symbol | Meaning | Toy value | Real Dilithium (ML-DSA-65 reference) |
|---|---|---|---|
| `n` | polynomial degree (ring = `Z_q[X]/(X^n+1)`) | 8 | 256 |
| `q` | coefficient modulus | small prime, `q ≡ 1 (mod 2n)` | `2^23 - 2^13 + 1` |
| `k, l` | module dimensions (`A` is `k×l`) | 2×2 (or 3×2) | 6×5 |
| `η` (eta) | bound on secret coefficients `s1, s2` | small (e.g. 2) | 2 or 4 |
| `γ1` | bound on commitment `y` / response `z` | derived, `≫ η·τ` | `2^17` or `2^19` |
| `τ` (tau) | number of ±1 coefficients in challenge `c` | small (e.g. 2–3 out of `n`) | 39 or 49 out of 256 |
| `β` | rejection threshold on `z` | `γ1 − τ·η` | scheme-defined |

Toy values should be chosen so:
- `q` is prime and `q ≡ 1 (mod 2n)` (enables clean `X^n+1` reduction; NTT not required at this scale).
- The challenge space size `C(n, τ) · 2^τ` is large enough that guessing `c` isn't trivial, while `n` stays small enough to print in full.

## 3. Ring arithmetic

Ring: `R_q = Z_q[X] / (X^n + 1)`.

Required operations:
- `add(a, b)` — coefficient-wise addition mod `q`.
- `mul(a, b)` — polynomial multiplication followed by reduction: repeatedly replace
  `X^n` with `-1` (not `+1`, since the modulus is `X^n+1`, not `X^n-1` as in the
  earlier NTRU example) and reduce coefficients mod `q`.
- `sample_small(bound)` — sample a polynomial with each coefficient drawn uniformly
  from `[-bound, bound]`.
- `sample_challenge(tau)` — sample a polynomial with exactly `tau` coefficients set
  to `±1` (positions and signs random) and the rest `0`.
- Matrix/vector versions of the above, for `k×l` matrices of ring elements.

All coefficients are stored reduced into a fixed representative range
(e.g. `(-q/2, q/2]`) to avoid the `-1 ≡ q-1` ambiguity bug encountered during
manual NTRU calculation earlier in this project's research phase.

## 4. Algorithms

### 4.1 KeyGen

```
A       ← R_q^{k×l}                     (uniform random matrix)
s1      ← sample_small(η)^l
s2      ← sample_small(η)^k
t       = A·s1 + s2                     (mod q)   ← a Module-LWE sample
pk      = (A, t)
sk      = (A, t, s1, s2)
```

### 4.2 Sign(sk, message)

```
loop:
    y  ← sample_small(γ1)^l
    w  = A·y                            (mod q)
    c  = H(w, message)  →  sample_challenge(τ), seeded by hash(w || message)
    z  = y + c·s1
    if ||z||_∞ ≥ γ1 − τ·η:               # rejection sampling
        continue                         # restart with fresh y
    return (z, c)
```

Log the number of restarts per signature — this reproduces the paper's
"~5 attempts on average" figure at whatever rate the toy parameters produce.

### 4.3 Verify(pk, message, (z, c))

```
if ||z||_∞ ≥ γ1 − τ·η:
    return REJECT
w' = A·z − c·t                          (mod q)
c' = H(w', message)
return ACCEPT if c' == c else REJECT
```

### 4.4 Broken variant (for the attack demo — see §5)

A second signer, `SignBroken`, identical to `Sign` **except**:
- no rejection-sampling check (always returns on the first attempt), **or**
- reuses the same `y` (and thus the same `w`) across two different messages.

This variant must be clearly isolated in its own module/function and never
imported by the honest `Sign`/`Verify` path, to avoid accidentally shipping
insecure code as if it were the real scheme.

## 5. Attack: forgery-derived SIS solution

Given two signatures produced with the **same `w`** (same `y`) but different
challenges, `(z, c)` and `(z', c')`, for the same or different messages:

```
A·(z − z') ≡ (c − c')·t                         (mod q)
substitute t = A·s1 + s2:
A·[(z − z') − (c − c')·s1] − (c − c')·s2 ≡ 0     (mod q)
```

Define `u = ( (z−z') − (c−c')·s1 ,  −(c−c')·s2 )`. Then:

```
[A | I]·u ≡ 0 (mod q),   u short and nonzero
```

`u` is a solution to the Module-SIS instance defined by `[A | I]`.

**Deliverable:** a script that, given a `SignBroken`-produced pair of signatures,
extracts `u` and verifies numerically that `[A|I]·u ≡ 0 (mod q)` and that `u`'s
coefficients are small — demonstrating the forgery-to-SIS reduction with real
numbers rather than only symbolically.

## 6. Size accounting

Report, in bytes, for the chosen toy parameters:
- Public key size: `|seed for A| + |t|` (compressed high-bits, if implemented) or raw `t`.
- Signature size: `|z| + |c| + |hint|` (hint vector optional — may be omitted at
  this toy scale if verification is designed not to need it).
- A comparison table against a real ECDSA (secp256k1) keypair/signature
  generated via a standard library, for the blog's size-comparison section.

## 7. Non-goals

- No NTT / fast multiplication — toy `n` is small enough for naive `O(n^2)` multiplication.
- No side-channel resistance, no constant-time arithmetic.
- No claim of matching real Dilithium's exact security level — toy parameters
  are chosen for pedagogical clarity, not any target bit-security.
- No hint-vector compression optimization (§5.7 "Optimizations" in the reference
  paper) unless time permits — explicitly marked optional in `plan.md`.
