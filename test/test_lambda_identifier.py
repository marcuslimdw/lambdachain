from operator import add, sub, mul, truediv, floordiv, mod, eq, gt, ge, lt, le, ne, neg
from typing import Callable

import pytest

from lambdachain.lambda_identifier import Lambda as _

ARITHMETIC_PARAMETERS = [0, 1, -3.0, 'value%s', [], True, None]
BINARY_ARITHMETIC_OPERATORS = [add, sub, mul, truediv, floordiv, mod, pow]
UNARY_ARITHMETIC_OPERATORS = [abs, neg]
COMPARISON_OPERATORS = [eq, gt, ge, lt, le, ne]


@pytest.mark.parametrize('forward', {True, False})
@pytest.mark.parametrize('op', BINARY_ARITHMETIC_OPERATORS)
@pytest.mark.parametrize('data', ARITHMETIC_PARAMETERS)
def test_binary_arithmetic_operators(forward, op, data):
    f = op(_, data) if forward else op(data, _)
    try:
        expected = op(3, data) if forward else op(data, 3)
        assert f(3) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(3)


@pytest.mark.parametrize('op', UNARY_ARITHMETIC_OPERATORS)
@pytest.mark.parametrize('data', ARITHMETIC_PARAMETERS)
def test_unary_arithmetic_operators(op, data):
    f = op(_)
    try:
        expected = op(data)
        assert f(data) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(data)


@pytest.mark.parametrize(['a', 'b'], zip(*[ARITHMETIC_PARAMETERS, ARITHMETIC_PARAMETERS]))
@pytest.mark.parametrize('op', [eq, gt, ge, lt, le, ne])
def test_comparison_operators(a, b, op):
    f = op(_, _)
    try:
        expected = op(a, b)
        assert f(a)(b) == expected

    except Exception as e:
        with pytest.raises(e.__class__):
            f(a)(b)


@pytest.mark.parametrize(['data', 'key', 'expected'], [('cake', 2, 'k')])
def test_getitem(data, key, expected):
    f = _[key]
    assert f(data) == expected


@pytest.mark.parametrize('data', [2, 'abc'])
def test_getattr(data):
    f = _.real
    try:
        expected = data.real
        assert f(data) == expected

    except Exception:
        with pytest.raises(ValueError):
            f(data)


def test_getattr_mistake():
    with pytest.raises(ValueError):
        _.join('a', 'b', 'c')


@pytest.mark.parametrize(['data', 'f', 'expected'],
                         [('abc', _.upper @ (), 'ABC'),
                          ('hello', _.count @ 'l', 2),
                          (',', _.join @ ('1', '2', '3'), '1,2,3')
                          ])
def test_getattr_call(data, f: Callable, expected):
    try:
        assert f(data) == expected

    except Exception as e:
        with pytest.raises(e.__class__):
            f(data)


@pytest.mark.parametrize(['a', 'b'], zip(*[ARITHMETIC_PARAMETERS, ARITHMETIC_PARAMETERS]))
@pytest.mark.parametrize('op', [add, sub, mod, eq])
def test_double(op, a, b):
    f = op(_, _)
    try:
        expected = op(a, b)
        assert f(a)(b) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(a)(b)


@pytest.mark.parametrize(['a', 'b'], zip(*[ARITHMETIC_PARAMETERS, ARITHMETIC_PARAMETERS]))
@pytest.mark.parametrize('op', [add, sub, mod, eq])
def test_rdouble(op, a, b):
    f = op(_, _)
    try:
        expected = op(b, a)
        assert f(b)(a) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(b)(a)


@pytest.mark.parametrize(['a', 'b'], zip(*[ARITHMETIC_PARAMETERS, ARITHMETIC_PARAMETERS]))
def test_and(a, b):
    f = _ & _
    assert f(a)(b) == (a and b)


@pytest.mark.parametrize(['a', 'b'], zip(*[ARITHMETIC_PARAMETERS, ARITHMETIC_PARAMETERS]))
def test_or(a, b):
    f = _ | _
    assert f(a)(b) == (a or b)


@pytest.mark.parametrize('data', ARITHMETIC_PARAMETERS)
def test_not(data):
    f = ~_
    assert f(data) == (not data)


def test_bool_conversion_fail():
    with pytest.raises(ValueError):
        assert _ and _

    with pytest.raises(ValueError):
        assert _ or _

    with pytest.raises(ValueError):
        assert not _


@pytest.mark.xfail
def test_chained_bool():
    f = _ & _ | _ & _
    assert not f(True)(True)(False)(False)
    assert f(True)(True)(False)(True)


@pytest.mark.xfail
def test_combined_filter():
    f = (_ % 2 == 0) & (_ > 5)
    assert list(filter(f, range(9))) == [6, 8]
