# PLAN.md — Build Plan for Dilithium-Lite

Reference: see `spec.md` for exact algorithms and parameters this plan implements.

## Milestones

### M1 — Ring arithmetic
- [X] Implement `add`, `mul` (with `X^n ≡ -1` reduction), coefficient mod-`q` reduction.
- [X] Implement `sample_small(bound)` and `sample_challenge(tau)`.
- [X] Unit test: pick two known small polynomials, multiply by hand (on paper),
      compare to code output. Reuse the manual NTRU-style verification method
      from the research phase (`f·f⁻¹ ≡ 1`-style checks) as a template.
- **Exit criteria:** ring multiplication matches hand-computed examples for at
  least 3 test cases, including one that wraps both `X^n` and `q`.

### M2 — KeyGen
- [X] Implement matrix sampling, `s1`, `s2`, and `t = A·s1 + s2`.
- [X] Sanity check: print `A, s1, s2, t` for a small run; confirm `t` shows no
      visible structure/pattern relative to `s1, s2` (informal "does it look
      random" check, not a statistical test).
- **Exit criteria met:** KeyGen runs deterministically given a fixed random seed
  (for reproducible tests) and non-deterministically otherwise.

M2 is implemented in `keygen.py`; its core invariant is the Module-LWE relation
`t = A·s1 + s2 (mod q)` with bounded `s1` and `s2`.

### M3 — Sign / Verify (honest path)
- [X] Implement `Sign` with rejection sampling and restart-counting.
- [X] Implement `Verify`.
- [X] Test: sign 100 messages, verify all succeed.
- [X] Test: tamper with one byte of a signed message, confirm verification fails.
- [X] Test: tamper with one coefficient of `z`, confirm verification fails.
- [X] Log and report average restart count across ≥100 signing runs.
- **Exit criteria met:** 100/100 honest verifications pass; all tamper tests correctly reject.

M3 is implemented in `sign.py`; its core logic protects fresh-`y` rejection sampling and commitment/challenge integrity.

### M4 — Attack demo
- [X] Implement `SignBroken` (no rejection check, or `y`-reuse variant), in an
      isolated module per `spec.md` §4.4.
- [X] Implement the extraction script: given two `SignBroken` outputs with shared
      `w`, compute `u` per the derivation in `spec.md` §5.
- [X] Verify numerically: `[A|I]·u ≡ 0 (mod q)` and report `||u||_∞`.
- [X] Confirm `u` is nonzero and its norm is small relative to `q` — i.e., a
      genuine (toy-scale) SIS solution, not a degenerate all-zero result.
- [X] Recover `s2` from `u`'s second half via `s2 = −u_2 / (c−c')` (ring
      inversion of `(c−c')`, same technique as the NTRU `f⁻¹` inversion),
      and confirm it matches the real `s2` from `KeyGen` — i.e., go beyond an
      abstract SIS witness and show the attack actually leaks the secret key.
- **Exit criteria met:** attack script reliably (across ≥10 trials) extracts a
  valid, nonzero, short `u` from `SignBroken` output; running the same script
  against honest `Sign` output correctly fails to produce a usable `u` (or is
  not even attempted, since `w` differs every time by design). The recovered
  `s2` matches the real secret key in all successful trials.

### M5 — Size accounting
- [X] Compute and print public key / signature byte sizes for the chosen toy parameters.
- [X] Generate one ECDSA (secp256k1) keypair + signature via a standard library
      for comparison.
- [X] Produce a small comparison table (toy Dilithium-lite vs. ECDSA vs., if time
      permits, published real-Dilithium sizes from `spec.md`'s reference table).
- **Exit criteria met:** table with three columns (this project / ECDSA / real ML-DSA reference) is generated and reads sensibly.

M5 is implemented in `sizes.py`; its core invariant is consistent byte counting for the chosen toy representation.

### M6 — Write-up (blog / portfolio post)
- [ ] Draft narrative per the structure agreed on: lead with the attack (M4),
      then unpack the theory, then the size comparison, with an explicit
      toy-parameters disclaimer.
- [ ] Pair each major code section with the corresponding hand-derived algebra
      (ring reduction example, the `A(z-z') = (c-c')t` derivation, etc.).
- [ ] Link back to blockchain/wallet context (Ethereum PQC migration discussion)
      in intro and conclusion.
- **Exit criteria:** `README.md` finalized and cross-linked to the post.

## Stack

- Python 3, no external crypto libraries for the core scheme (the point is to
  implement the math, not call a library that already does it).
- `ecdsa` (or `cryptography`) library only for the M5 comparison baseline.
- Plain `pytest` (or even just `assert`-based scripts) for the tests listed above.
- No NTT, no C extensions — pure Python is fine at this toy scale.

## Explicit scope cuts (see `spec.md` §7)

If time is short, cut in this order: (1) hint-vector compression, (2) size
comparison against published real-ML-DSA numbers (keep only the ECDSA
comparison), (3) restart-count statistics beyond a single reported average.
Do **not** cut M4 (the attack demo) — it's the core deliverable that
distinguishes this from a plain "implemented a scheme" exercise.

## Time estimate

Given prior familiarity with all the underlying math (ring arithmetic, LWE,
SIS, the forgery reduction — already derived by hand before this plan was
written): M1–M3 roughly one focused session each; M4 is the most
algebra-sensitive and may need a second pass; M5–M6 are light.
