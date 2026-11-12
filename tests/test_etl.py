import pandas as pd
from etl.copy_raw_to_ch import _to_str_or_none

def test_to_str_or_none():
    """Проверяем, что функция корректно превращает NaN/None в None, а числа в строки."""
    assert _to_str_or_none(None) is None
    assert _to_str_or_none(pd.NA) is None
    assert _to_str_or_none(float('nan')) is None
    assert _to_str_or_none(123) == "123"
    assert _to_str_or_none("hello") == "hello"
