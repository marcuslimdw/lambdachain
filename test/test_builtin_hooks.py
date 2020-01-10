import pytest

from lambdachain.builtin_hooks import bool, int, float, str, len, isinstance
from lambdachain.lambda_identifier import Lambda as _


@pytest.mark.parametrize('f', [bool, bool(_)])
@pytest.mark.parametrize(['data', 'expected'], [(0, False),
                                                (1, True),
                                                ('', False),
                                                ('0', True),
                                                ([], False),
                                                ([''], True),
                                                (None, False),
                                                ({None}, True)])
def test_bool(f, data, expected):
    assert f(data) == expected


@pytest.mark.parametrize('f', [int, int(_)])
@pytest.mark.parametrize(['data', 'expected'], [('1', 1),
                                                (1.2, 1)])
def test_int(f, data, expected):
    assert f(data) == expected


@pytest.mark.parametrize('f', [float, float(_)])
@pytest.mark.parametrize(['data', 'expected'], [(1, 1.0),
                                                ('1.2', 1.2)])
def test_float(f, data, expected):
    assert f(data) == expected


@pytest.mark.parametrize('f', [str, str(_)])
@pytest.mark.parametrize(['data', 'expected'], [(1, '1'),
                                                (1.2, '1.2'),
                                                (['a', 'b'], "['a', 'b']"),
                                                (None, 'None')])
def test_str(f, data, expected):
    assert str(data) == expected


@pytest.mark.parametrize(['f', 'data', 'expected'], [(str(_) + 'b', 'a', 'ab'),
                                                     (float(_) + 3, '12', 15.0),
                                                     (~bool(_), [], True),
                                                     (len(_) * 2, [1, 2, 3], 6)])
def test_as_lambda_identifiers(f, data, expected):
    result = f(data)
    assert f(data) == expected and type(result) == type(expected)


@pytest.mark.parametrize(['data', 'types', 'expected'], [(1, int, True),
                                                         (1, (int, float), True),
                                                         ('a', (int, float), False)])
def test_isinstance(data, types, expected):
    assert isinstance(data, types) == expected


@pytest.mark.xfail
@pytest.mark.parametrize(['data', 'expected'], [(True, bool),
                                               (2, int),
                                               (3.0, float),
                                               ('a', str)])
def test_type_comparison(data, expected):
    assert type(data) == expected
