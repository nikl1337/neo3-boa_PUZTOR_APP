from typing import Any

from boa3.builtin import public


@public
def main(a: Any) -> bool:
    b = False

    if a:
        b = True
    return b
