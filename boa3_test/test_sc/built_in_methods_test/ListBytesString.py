from typing import List, Union

from boa3.builtin import public


@public
def main(x: Union[bytes, str]) -> List[Union[int, str]]:
    a = 'unit test'
    b = b'unit test'

    return list(x)
