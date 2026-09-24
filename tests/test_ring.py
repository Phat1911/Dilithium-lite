import random

from ring import Ring

RING = Ring(n=8, q=17)

def test_addition_and_centered_reduction():
    assert RING.add((8, 8, 0, 0, 0, 0, 0, 0), (1, 2, 0, 0, 0, 0, 0, 0)) == (-8, -7, 0, 0, 0, 0, 0, 0)

def test_multiplication_wraps_x_to_the_n_with_negative_sign():
    assert RING.mul((0, 0, 0, 0, 0, 0, 0, 1), (0, 1, 0, 0, 0, 0, 0, 0)) == (-1, 0, 0, 0, 0, 0, 0, 0)

def test_hand_computed_products_cover_three_cases_and_modulus_wrap():
    assert RING.mul((1, 1, 0, 0, 0, 0, 0, 0), (1, -1, 0, 0, 0, 0, 0, 0)) == (1, 0, -1, 0, 0, 0, 0, 0)
    assert RING.mul((0, 0, 0, 0, 0, 0, 0, 1), (0, 0, 0, 0, 0, 0, 0, 1)) == (0, 0, 0, 0, 0, 0, -1, 0)
    assert RING.mul((8, 0, 0, 0, 0, 0, 0, 0), (3, 0, 0, 0, 0, 0, 0, 0)) == (7, 0, 0, 0, 0, 0, 0, 0)

def test_small_and_challenge_sampling_bounds_and_weight():
    rng = random.Random(1234)
    small = RING.sample_small(2, rng)
    challenge = RING.sample_challenge(3, rng)
    assert all(-2 <= value <= 2 for value in small)
    assert sum(value != 0 for value in challenge) == 3
    assert all(value in (-1, 0, 1) for value in challenge)

def test_matrix_vector_multiplication():
    one = (1, 0, 0, 0, 0, 0, 0, 0)
    x = (0, 1, 0, 0, 0, 0, 0, 0)
    matrix = ((one, x), (x, one))
    assert RING.matrix_vector_mul(matrix, (one, one)) == ((1, 1, 0, 0, 0, 0, 0, 0),) * 2
