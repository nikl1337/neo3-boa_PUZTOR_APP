from boa3.builtin.compile_time import public


@public
def bytes_to_int() -> int:
    return bytearray.to_int(bytearray(b'\x01\x02'))
