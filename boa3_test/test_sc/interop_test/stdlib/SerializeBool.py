from boa3.builtin.compile_time import public
from boa3.builtin.interop.stdlib import serialize


@public
def serialize_bool() -> bytes:
    return serialize(True)
