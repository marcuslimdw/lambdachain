from operator import add, sub, mod, eq

import pytest

from lambdachain.lambda_identifier import Lambda as _

ARITHMETIC_PARAMETERS = [0, 1, -3.0, 'value', [1], True, None]


@pytest.mark.parametrize('data', ARITHMETIC_PARAMETERS)
def test_add(data):
    f = (_ + data)
    try:
        expected = 1 + data
        assert f(1) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(1)


@pytest.mark.parametrize('data', ARITHMETIC_PARAMETERS)
def test_radd(data):
    f = (data + _)
    try:
        expected = data + 1
        assert f(1) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(1)


@pytest.mark.parametrize('data', ARITHMETIC_PARAMETERS)
def test_sub(data):
    f = (_ - data)
    try:
        expected = 1 - data
        assert f(1) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(1)


@pytest.mark.parametrize('data', ARITHMETIC_PARAMETERS)
def test_rsub(data):
    f = (data - _)
    try:
        expected = data - 1
        assert f(1) == expected

    except AssertionError:
        raise

    except Exception as e:
        with pytest.raises(e.__class__):
            f(1)


@pytest.mark.parametrize(['a', 'b'], zip(*[ARITHMETIC_PARAMETERS, ARITHMETIC_PARAMETERS]))
def test_eq(a, b):
    f = (_ == _)
    expected = (a == b)
    # noinspection PyCallingNonCallable
    assert f(a)(b) == expected


@pytest.mark.parametrize(['a', 'b'], zip(*[ARITHMETIC_PARAMETERS, ARITHMETIC_PARAMETERS]))
def test_ne(a, b):
    f = (_ != _)
    expected = (a != b)
    # noinspection PyCallingNonCallable
    assert f(a)(b) == expected


@pytest.mark.parametrize('data', [2, 'abc'])
def test_getattr(data):
    f = _.real
    try:
        expected = data.real
        assert f(data) == expected

    except Exception as e:
        with pytest.raises(ValueError):
            f(data)


@pytest.mark.parametrize('data', [2, 'abc'])
def test_getattr_call(data):
    f = _.upper @ ()
    try:
        expected = data.upper()
        assert f(data) == expected

    except Exception as e:
        with pytest.raises(ValueError):
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
