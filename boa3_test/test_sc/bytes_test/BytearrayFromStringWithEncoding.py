from boa3.builtin.compile_time import public


@public
def main(a: str) -> bytearray:
    b: bytearray = bytearray(a, 'utf-8')

    return b
