import random

from keygen import KeyGenerator, keygen
from ring import Ring


def test_keygen_is_deterministic_for_a_fixed_seed():
    first = keygen(rng=random.Random(2026))
    second = keygen(rng=random.Random(2026))
    assert first == second


def test_keygen_shapes_bounds_and_module_lwe_relation():
    ring = Ring()
    pair = KeyGenerator(ring, k=2, l=2, eta=2, rng=random.Random(7)).generate()
    public = pair.public_key
    secret = pair.secret_key

    assert len(public.A) == 2
    assert all(len(row) == 2 for row in public.A)
    assert len(public.t) == len(secret.s2) == 2
    assert len(secret.s1) == 2
    assert all(abs(value) <= 2 for poly in secret.s1 + secret.s2 for value in poly)
    assert public.t == ring.vector_add(ring.matrix_vector_mul(public.A, secret.s1), secret.s2)


def test_matrix_sampling_is_uniformly_reduced_and_dimension_checked():
    generator = KeyGenerator(k=3, l=2, rng=random.Random(11))
    matrix = generator.sample_matrix()
    assert len(matrix) == 3
    assert all(len(row) == 2 for row in matrix)
    assert all(-generator.ring.q // 2 <= value <= generator.ring.q // 2 for row in matrix for poly in row for value in poly)
