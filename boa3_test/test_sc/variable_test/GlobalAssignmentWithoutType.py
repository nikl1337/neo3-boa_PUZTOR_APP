from boa3.builtin.compile_time import public

a = 10


@public
def Main() -> int:
    return a
