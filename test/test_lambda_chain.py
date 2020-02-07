from functools import reduce
from itertools import groupby
from operator import add

import pytest

from lambdachain.builtin_hooks import len
from lambdachain.lambda_chain import LambdaChain as LC, uncurry, curry
from lambdachain.lambda_identifier import Lambda as _


@pytest.mark.parametrize(['data', 'genexp', 'expected'],
                         [([2, 4, 6], (i // 2 for i in _), [1, 2, 3]),
                          ([[1, 2], [3, 4], [5, 6]], ([i * 2 for i in s] for s in _), [[2, 4], [6, 8], [10, 12]]),
                          ([[1, 2], [3, 4], [5, 6]], (i * 3 for s in _ for i in s), [3, 6, 9, 12, 15, 18]),
                          (groupby([1, 3, 4, 8], _ % 2), ((k, list(g)) for k, g in _), [(1, [1, 3]), (0, [4, 8])])
                          ])
def test_apply(data, genexp, expected):
    assert LC(data).apply(genexp).force() == expected


@pytest.mark.parametrize(['f', 'data'],
                         [(lambda: 1, ()),
                          (lambda x: x + 2, (1,)),
                          (lambda x, y: x / y, (3, 7)),
                          (lambda x, y, z: str(x % y) + z, (8, 5, '8'))
                          ])
def test_curry(f, data):
    if len(data) == 0:
        assert curry(f) == f

    else:
        assert reduce(lambda next_f, arg: next_f(arg), data, curry(f)) == f(*data)


@pytest.mark.parametrize(['data', 'start', 'step', 'expected'], [(['a', 'b', 'c'], 2, 2,
                                                                  [(2, 'a'), (4, 'b'), (6, 'c')]),
                                                                 ([True, True, False], 0, 1,
                                                                  [(0, True), (1, True), (2, False)])])
def test_enumerate(data, start, step, expected):
    assert LC(data).enumerate(start, step).force() == expected


@pytest.mark.parametrize(['data', 'f', 'expected'], [(range(-5, 5), _ % 2 == 0, [-4, -2, 0, 2, 4])])
def test_filter(data, f, expected):
    assert LC(data).filter(_ % 2 == 0).force() == expected


@pytest.mark.parametrize(['data', 'initial_value'], [(range(3, 7), -2)])
@pytest.mark.parametrize('f', [add])
def test_folds(data, initial_value, f):
    chain = LC(data).persist()
    f_curried = curry(f)
    fold_result = chain.force.fold(f, initial_value)
    foldc_result = chain.force.foldc(f_curried)(initial_value)
    expected = reduce(f, data, initial_value)
    assert fold_result == foldc_result == expected


@pytest.mark.parametrize(['data', 'f', 'combine', 'expected'],
                         [([0, 2, 1, 3, 2], _ % 2, True,
                           [(0, [0, 2, 2]), (1, [1, 3])]),
                          ([0, 2, 1, 3, 2], _ % 2, False,
                           [(0, [0, 2]), (1, [1, 3]), (0, [2])]),
                          (['karma', 'pie', 'sty', 'cake', 'laugh'], len, True,
                           [(5, ['karma', 'laugh']), (3, ['pie', 'sty']), (4, ['cake'])]),
                          (['karma', 'pie', 'sty', 'cake', 'laugh'], len, False,
                           [(5, ['karma']), (3, ['pie', 'sty']), (4, ['cake']), (5, ['laugh'])])
                          ])
def test_groupby(data, f, combine, expected):
    assert LC(data).groupby(f, combine).force() == expected


def test_iter():
    assert list(LC((1, 2, 3))) == [1, 2, 3]


@pytest.mark.parametrize(['data', 'f', 'expected'], [(range(-5, 5, 3), _ + 1, [-4, -1, 2, 5])])
def test_map(data, f, expected):
    assert LC(data).map(f).force() == expected


@pytest.mark.parametrize(['data', 'f', 'expected'], [(range(-5, 5), _ % 2 == 0, [-5, -3, -1, 1, 3])])
def test_reject(data, f, expected):
    assert LC(data).reject(_ % 2 == 0).force() == expected


@pytest.mark.parametrize(['f', 'data'],
                         [(lambda: 1, ()),
                          (lambda x: x + 2, (1,)),
                          (lambda x: lambda y: x / y, (3, 7)),
                          (lambda x: lambda y: lambda z: str(x % y) + z, (8, 5, '8'))
                          ])
def test_uncurry(f, data):
    if len(data) == 0:
        assert uncurry(f) == f

    else:
        assert uncurry(f)(*data) == reduce(lambda next_f, arg: next_f(arg), data, f)


@pytest.mark.parametrize(['data', 'expected'],
                         [([3, 0, 5, 7, 0, 4, 3, 4], [3, 0, 5, 7, 4]),
                          pytest.param([[0], [2], [0], [1], [2], [0]], [[0], [2], [1]])
                          ])
@pytest.mark.parametrize('hashable', [True, False])
def test_unique(data, expected, hashable):
    assert LC(data).unique(hashable).force() == expected


@pytest.mark.parametrize(['data', 'f', 'expected'],
                         [([3, 0, 5, 7, 0, 4, 3, 4], _ % 3, [3, 5, 7]),
                          (['apple', 'scream', 'white', 'bay', 'pea'], len, ['apple', 'scream', 'bay']),
                          ([[0, 1], [0, 2], [2, 0], [1, 1], [2, 1], [1, 0], [0, 1]], _[:1], [[0, 1], [2, 0], [1, 1]])
                          ])
@pytest.mark.parametrize('hashable', [True, False])
def test_unique_by(data, expected, f, hashable):
    assert LC(data).unique_by(f, hashable).force() == expected


@pytest.mark.parametrize(['data', 'zip_data', 'expected'],
                         [(['alpha', 'bravo', 'charlie'], [True, True, False],
                           [('alpha', True), ('bravo', True), ('charlie', False)])
                          ])
def test_zip(data, zip_data, expected):
    assert LC(data).zip(zip_data).force() == expected


class TestForce:

    @pytest.mark.parametrize(['data', 'expected'],
                             [([], True),
                              ([0, None], False),
                              ([1, 0], False),
                              ([True, 'a'], True)])
    def test_all(self, data, expected):
        assert LC(data).force.all() == expected

    @pytest.mark.parametrize(['data', 'expected'],
                             [([], False),
                              ([0, None], False),
                              ([1, 0], True),
                              ([True, 'a'], True)])
    def test_any(self, data, expected):
        assert LC(data).force.any() == expected

    def test_force(self):
        assert LC((1, 2, 3)).force() == [1, 2, 3]

    def test_foreach(self):
        def print(a, b):
            result.append((a, b))

        result = []
        LC([1, 2, 3]).force.foreach(print, b=0)
        assert result == [(1, 0), (2, 0), (3, 0)]

    @pytest.mark.parametrize(['data', 'separator', 'expected'],
                             [(['a', 'b', 'c'], '.', 'a.b.c')])
    def test_join(self, data, separator, expected):
        assert LC(data).force.join(separator) == expected

    @pytest.mark.parametrize(['data', 'initial', 'expected'],
                             [([1, 2, 3], 'a', 'aaaaaa'),
                              ([4, 5, 6], 1, 120)])
    def test_product(self, data, initial, expected):
        assert LC(data).force.product(initial) == expected

    @pytest.mark.parametrize(['data', 'initial', 'expected'],
                             [([2, 4, 6], 3, 15),
                              ({0, 10, -3}, -2, 5)])
    def test_sum(self, data, initial, expected):
        assert LC(data).force.sum(initial) == expected
