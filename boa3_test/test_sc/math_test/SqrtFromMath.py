from math import sqrt

from boa3.builtin.compile_time import public


@public
def main(x: int) -> int:
    return sqrt(x)
