from functools import reduce
from itertools import groupby
from operator import add

import pytest

from lambdachain.lambda_chain import LambdaChain, uncurry, curry
from lambdachain.lambda_identifier import Lambda as _


@pytest.mark.parametrize(['data', 'f', 'expected'],
                         [(range(-5, 5, 3), _ + 1, [-4, -1, 2, 5])])
def test_map(data, f, expected):
    assert LambdaChain(data).map(f).force(list) == expected


@pytest.mark.parametrize(['data', 'f', 'expected'],
                         [(range(-5, 5), _ % 2 == 0, [-4, -2, 0, 2, 4])])
def test_filter(data, f, expected):
    assert LambdaChain(data).filter(_ % 2 == 0).force(list) == expected


@pytest.mark.parametrize(['data', 'initial_value'], [(range(3, 7), -2)])
@pytest.mark.parametrize('f', [add])
def test_folds(data, initial_value, f):
    chain = LambdaChain(data)
    f_curried = curry(f)
    assert chain.fold(f, initial_value) == chain.foldc(f_curried)(initial_value) == reduce(f, data, initial_value)


@pytest.mark.parametrize(['data', 'expected', 'ordered'],
                         [([3, 0, 0, 7, 4, 2, 4], [0, 2, 4, 3, 7], False),
                          ([3, 0, 0, 7, 4, 2, 4], [3, 0, 7, 4, 2], True)])
def test_unique(data, expected, ordered):
    result = LambdaChain(data).unique(ordered)
    if ordered:
        assert result.force(list) == expected

    else:
        assert result.force(set) == set(expected)


def test_zip():
    assert LambdaChain(['t', 'u', 'v']).zip([2, 5, 8]).force(dict) == {'t': 2, 'u': 5, 'v': 8}


def test_enumerate():
    assert LambdaChain(['t', 'u', 'v']).enumerate(2).force(dict) == {2: 't', 3: 'u', 4: 'v'}


@pytest.mark.parametrize(['data', 'genexp', 'force', 'expected'],
                         [([2, 4, 6], (i // 2 for i in _), list, [1, 2, 3]),
                          ([[1, 2], [3, 4], [5, 6]], ([i * 2 for i in s] for s in _), list, [[2, 4], [6, 8], [10, 12]]),
                          ([[1, 2], [3, 4], [5, 6]], (i * 3 for s in _ for i in s), list, [3, 6, 9, 12, 15, 18]),
                          (groupby([1, 3, 4, 8], _ % 2), ((k, list(g)) for k, g in _), dict, {1: [1, 3], 0: [4, 8]})
                          ])
def test_apply(data, genexp, force, expected):
    assert LambdaChain(data).apply(genexp).force(force) == expected


def test_force():
    assert LambdaChain((1, 2, 3)).force(list) == [1, 2, 3]


@pytest.mark.parametrize(['f', 'data'], [(lambda: 1, ()),
                                         (lambda x: x + 2, (1,)),
                                         (lambda x, y: x / y, (3, 7)),
                                         (lambda x, y, z: str(x % y) + z, (8, 5, '8'))])
def test_curry(f, data):
    if len(data) == 0:
        assert curry(f) == f

    else:
        assert reduce(lambda next_f, arg: next_f(arg), data, curry(f)) == f(*data)


@pytest.mark.parametrize(['f', 'data'], [(lambda: 1, ()),
                                         (lambda x: x + 2, (1,)),
                                         (lambda x: lambda y: x / y, (3, 7)),
                                         (lambda x: lambda y: lambda z: str(x % y) + z, (8, 5, '8'))])
def test_uncurry(f, data):
    if len(data) == 0:
        assert uncurry(f) == f

    else:
        assert uncurry(f)(*data) == reduce(lambda next_f, arg: next_f(arg), data, f)
