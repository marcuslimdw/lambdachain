from builtins import bool as _bool, int as _int, float as _float, str as _str

import pytest

from lambdachain.builtin_hooks import bool, int, float, str, len, isinstance, type
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


@pytest.mark.parametrize(['data', 'expected'], [(True, _bool),
                                                (2, _int),
                                                (3.0, _float),
                                                ('a', _str)])
def test_type_comparison(data, expected):
    assert type(data) == expected


def test_new_type():
    def test_init(self, *it):
        super(self.__class__, self).__init__(it)

    new_type = type('new_type', (list,), {'__init__': test_init})
    assert new_type.__name__ == 'new_type'
    assert new_type.__bases__ == (list,)
    assert new_type(1, 2, 3) == [1, 2, 3]


def test_type_failure():
    with pytest.raises(TypeError):
        type(1, 2)
