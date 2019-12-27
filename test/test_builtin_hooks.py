import pytest

from lambdachain.builtin_hooks import bool, int, float, str
from lambdachain.lambda_identifier import Lambda as _


@pytest.mark.parametrize(['data', 'expected'], [(0, False),
                                                (1, True),
                                                ('', False),
                                                ('0', True),
                                                ([], False),
                                                ([''], True),
                                                (None, False),
                                                ({None}, True)])
def test_bool_normal(data, expected):
    assert bool(data) == expected


@pytest.mark.parametrize(['data', 'expected'], [(0, False),
                                                (1, True),
                                                ('', False),
                                                ('0', True),
                                                ([], False),
                                                ([''], True),
                                                (None, False),
                                                ({None}, True)])
def test_bool_lambda(data, expected):
    assert bool(_)(data) == expected


@pytest.mark.parametrize(['data', 'expected'], [('1', 1),
                                                (1.2, 1)])
def test_int_normal(data, expected):
    assert int(data) == expected


@pytest.mark.parametrize(['data', 'expected'], [('1', 1),
                                                (1.2, 1)])
def test_int_lambda(data, expected):
    assert int(_)(data) == expected


@pytest.mark.parametrize(['data', 'expected'], [(1, 1.0),
                                                ('1.2', 1.2)])
def test_float_normal(data, expected):
    assert float(data) == expected


@pytest.mark.parametrize(['data', 'expected'], [(1, 1.0),
                                                ('1.2', 1.2)])
def test_float_lambda(data, expected):
    assert float(_)(data) == expected


@pytest.mark.parametrize(['data', 'expected'], [(1, '1'),
                                                (1.2, '1.2'),
                                                (['a', 'b'], "['a', 'b']"),
                                                (None, 'None')])
def test_str_normal(data, expected):
    assert str(data) == expected


@pytest.mark.parametrize(['data', 'expected'], [(1, '1'),
                                                (1.2, '1.2'),
                                                (['a', 'b'], "['a', 'b']"),
                                                (None, 'None')])
def test_str_lambda(data, expected):
    assert str(_)(data) == expected
