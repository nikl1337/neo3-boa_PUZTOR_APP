from boa3.builtin.compile_time import public


@public
def add_six(a: int) -> int:
    return 1 + a + 5
