from typing import Any, Tuple

from boa3.builtin import public


@public
def main(a: Tuple[Any], value: Any, start: int) -> int:
    return a.index(value, start)
