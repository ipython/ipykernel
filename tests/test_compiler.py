"""Tests for the compiler helpers."""

import pytest

from ipykernel.compiler import get_tmp_hash_seed, murmur2_x86


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        # known values, must never change: cell filenames depend on them
        ("", 3990065800),
        ("print('hello')", 3900465672),
        ("héllo", 3844570329),
        ("日本語", 584879906),
    ],
)
def test_murmur2_known_values(data, expected):
    assert murmur2_x86(data, get_tmp_hash_seed()) == expected


def test_murmur2_tail_lengths():
    # exercise all remainder branches (length % 4 == 0, 1, 2, 3)
    seed = get_tmp_hash_seed()
    results = {murmur2_x86("x" * n, seed) for n in range(9)}
    assert len(results) == 9
