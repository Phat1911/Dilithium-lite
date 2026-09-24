import random

from attack_demo import extract
from broken_sign import sign_pair
from keygen import keygen
from sign import Signer, verify
from sizes import comparison_table, toy_sizes


def test_m3_honest_signatures_and_tamper_rejection():
    pair = keygen(rng=random.Random(10))
    signer = Signer(pair.secret_key, rng=random.Random(11))
    for index in range(100):
        message = f"message-{index}".encode()
        signature = signer.sign(message)
        assert verify(pair.public_key, message, signature)
        assert not verify(pair.public_key, message + b"!", signature)
        tampered_z = list(signature.z)
        tampered_z[0] = (tampered_z[0][0] + 1,) + tampered_z[0][1:]
        tampered = type(signature)(tuple(tampered_z), signature.c, signature.w, signature.tag)
        assert not verify(pair.public_key, message, tampered)


def test_m4_extracts_nonzero_sis_witness_and_s2():
    successes = 0
    seed = 0
    while successes < 10:
        pair = keygen(rng=random.Random(seed))
        try:
            first, second = sign_pair(pair.secret_key, b"first", b"second", rng=random.Random(seed + 100))
        except StopIteration:
            seed += 1
            continue
        witness, residual, recovered = extract(pair, first, second)
        assert any(value for poly in witness for value in poly)
        assert max(abs(value) for poly in witness for value in poly) < 17
        assert all(value == 0 for poly in residual for value in poly)
        assert recovered == pair.secret_key.s2
        successes += 1
        seed += 1


def test_m5_size_table_has_three_rows():
    table = comparison_table()
    assert len(table) == 3
    assert toy_sizes()["public_key"] > 0
    assert table[0]["signature_bytes"] > 0
