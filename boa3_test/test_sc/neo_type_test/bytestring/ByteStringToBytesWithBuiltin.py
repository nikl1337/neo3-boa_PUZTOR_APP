from boa3.builtin.compile_time import public
from boa3.builtin.type import ByteString


@public
def to_bytes(arg: ByteString) -> bytes:
    return ByteString.to_bytes(arg)
