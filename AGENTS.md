# Agent Guidance

## Project structure and conventions

- `spec.md` is the source of truth for toy parameters, algorithms, and scope; `plan.md` (also referred to as `PLAN.md`) tracks milestones and explicitly marked core logic.
- Python 3, pure Python for the scheme's math; keep the implementation small and inspectable. Use standard-library randomness/hash functionality as specified by the implementation, and reserve `ecdsa`/`cryptography` for the size-comparison baseline only.
- Organize ring arithmetic, KeyGen, and honest Sign/Verify as reusable code; keep `SignBroken` and SIS extraction isolated from the honest signing/verification path. `demo.py` and `attack_demo.py` are planned entry points. Tests may use `pytest` or focused assertion scripts, following the spec and plan.
- Store polynomial coefficients in one documented representative range consistently. Keep toy parameters explicit and reproducible in tests (fixed seed where needed); normal key generation/signing must remain randomized.

## Rules

- This is a pedagogical toy, not production cryptography: parameters provide no real security, and implementation is not constant-time or side-channel resistant. Never describe it as production-ready or use it for real keys, signatures, or funds.
- Preserve the specified ring `Z_q[X]/(X^n+1)`: reduction of `X^n` changes its sign. Preserve the required prime/modulus relation and coefficient bounds when selecting toy parameters.
- Honest signing must retain rejection sampling and fresh `y` per attempt. Keep broken signing variants clearly isolated and labeled; never route honest Sign/Verify through them.
- Preserve the attack demo's algebraic requirements: shared `w` for the broken-signature pair, and verify the extracted vector is nonzero, short, and satisfies `[A | I]·u ≡ 0 (mod q)`.
- Do not add NTT, constant-time, production-security, or other out-of-scope claims/features; hint compression and published ML-DSA size comparison are optional as specified in `plan.md`.

## Default workflow

- After any code change, run the relevant tests and show their result before claiming completion. If tests cannot run, state why and report what was run instead.
- For code marked **core logic** in `PLAN.md` (or `plan.md`), explain what it does and which risk or invariant it protects.
- Do not deploy, publish, commit, push, or make external changes unless I explicitly ask.
- After each milestone, mark/comment at where that milestone is implemented and check the completed tasks in plan.md after each milestone.